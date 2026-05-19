#!/usr/bin/env python3
"""Analyze skills by running OpenCode with extended prompts."""
import argparse, os, re, yaml, subprocess, socket, time, json
from pathlib import Path

SKILL_DIRS = ["contribute", "extend", "frameworks", "languages", "tool"]
SKILL_FILE = "SKILL.md"

def parse_ndjson_response(output: str) -> str:
    text_parts = []
    for line in output.strip().split(chr(10)):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if event.get("type") == "text":
                part = event.get("part", {})
                if part.get("type") == "text":
                    text = part.get("text", "")
                    if text:
                        text_parts.append(text)
        except json.JSONDecodeError:
            continue
    return "".join(text_parts)

ANALYSIS_DIR = Path("./analysis")
FRONTEND_MATTER_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---", re.DOTALL)
MODEL = "regolo/minimax-m2.5"
SCORE_THRESHOLD = 0.7
OPENCODE_SERVER_HOST = "127.0.0.1"
OPENCODE_SERVER_PORT = 18889

def is_port_open(host: str, port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def start_opencode_server():
    if is_port_open(OPENCODE_SERVER_HOST, OPENCODE_SERVER_PORT):
        print(f"ℹ Using existing server at http://{OPENCODE_SERVER_HOST}:{OPENCODE_SERVER_PORT}")
        return {"host": OPENCODE_SERVER_HOST, "port": OPENCODE_SERVER_PORT, "process": None}
    try:
        process = subprocess.Popen(
            ["opencode", "serve", "--hostname", OPENCODE_SERVER_HOST, "--port", str(OPENCODE_SERVER_PORT)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=Path.cwd()
        )
        for _ in range(75):
            if is_port_open(OPENCODE_SERVER_HOST, OPENCODE_SERVER_PORT):
                print(f"✅ Started server at http://{OPENCODE_SERVER_HOST}:{OPENCODE_SERVER_PORT}")
                return {"host": OPENCODE_SERVER_HOST, "port": OPENCODE_SERVER_PORT, "process": process}
            time.sleep(0.2)
        process.kill()
        raise RuntimeError("Server failed to start")
    except Exception as e:
        raise RuntimeError(f"Failed to start server: {e}")

def extract_skill_metadata(skill_path: Path) -> dict | None:
    try:
        content = skill_path.read_text(encoding="utf-8")
        match = FRONTEND_MATTER_RE.match(content)
        if not match:
            return None
        frontmatter = match.group(1)
        data = yaml.safe_load(frontmatter)
        if not data:
            return None
        return {"name": data.get("name", ""), "description": data.get("description", ""), "path": str(skill_path)}
    except Exception:
        return None

def build_prompt(skill_meta: dict) -> str:
    return f"""Read the skill file from {skill_meta['path']} and explain how to use this skill.
Description: {skill_meta.get('description', '')}
Provide a code example."""

def run_opencode_cli(prompt: str, skill_name: str) -> tuple[str, int]:
    try:
        result = subprocess.run(["opencode", "run", "--model", MODEL, "--format", "json", prompt],
            capture_output=True, text=True, timeout=180, cwd=Path.cwd(), env={**os.environ})
        output = result.stdout + result.stderr
        parsed = parse_ndjson_response(output)
        if parsed:
            return parsed, result.returncode
        return output, result.returncode
    except subprocess.TimeoutExpired:
        return "Timeout", 124
    except Exception as e:
        return f"Error: {e}", 1

def delete_session(server_info: dict, session_id: str):
    """Delete an opencode session via HTTP API."""
    import http.client
    try:
        conn = http.client.HTTPConnection(server_info['host'], server_info['port'], timeout=10)
        conn.request("DELETE", f"/session/{session_id}")
        conn.getresponse().read()
        conn.close()
    except Exception:
        pass

def _http_request(server_info: dict, method: str, path: str, body: str | None = None, timeout: int = 180):
    """Make a single HTTP request on a fresh connection."""
    import http.client
    conn = http.client.HTTPConnection(server_info['host'], server_info['port'], timeout=timeout)
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=body, headers=headers)
    resp = conn.getresponse()
    return resp, conn

def run_opencode_server(prompt: str, skill_name: str, server_info: dict) -> tuple[str, int, str | None]:
    import http.client
    # Health check on a fresh connection
    try:
        resp, conn = _http_request(server_info, "GET", "/global/health", timeout=5)
        conn.close()
        if resp.status != 200:
            raise Exception(f"Health check returned {resp.status}")
    except Exception as e:
        print(f"  ⚠️  Server not responding, using CLI: {e}")
        resp_text, code = run_opencode_cli(prompt, skill_name)
        return resp_text, code, None
    # Create session on a fresh connection
    try:
        resp, conn = _http_request(server_info, "POST", "/session", body=json.dumps({"title": skill_name}))
        session = json.loads(resp.read().decode())
        conn.close()
        session_id = session.get("id")
        if not session_id:
            raise Exception("No session ID")
    except Exception as e:
        print(f"  ⚠️  Failed to create session ({e}), using CLI")
        resp_text, code = run_opencode_cli(prompt, skill_name)
        return resp_text, code, None
    # Send message on a fresh connection
    try:
        resp, conn = _http_request(server_info, "POST", f"/session/{session_id}/message", body=json.dumps({"parts": [{"type": "text", "text": prompt}]}))
        result_data = resp.read().decode()
        conn.close()
        parsed = parse_ndjson_response(result_data)
        if parsed:
            return parsed, 0, session_id
        return result_data, 0, session_id
    except Exception as e:
        print(f"  ⚠️  HTTP API failed ({e}), using CLI")
        resp_text, code = run_opencode_cli(prompt, skill_name)
        return resp_text, code, session_id

def evaluate_response(skill_name: str, response: str) -> dict:
    eval_prompt = f"""Evaluate this response for {skill_name} skill:
{response}
Score: 1.0 if excellent, 0.7 if good, 0.5 if partial, 0.0 if incorrect."""
    try:
        result = subprocess.run(["opencode", "run", "--model", MODEL, "--format", "json", eval_prompt],
            capture_output=True, text=True, timeout=300, cwd=Path.cwd())
        raw_output = result.stdout + result.stderr
        eval_response = parse_ndjson_response(raw_output) or raw_output
    except subprocess.TimeoutExpired:
        return {"evaluation": "Evaluation timed out", "score": 0.0}
    except Exception as e:
        return {"evaluation": f"Evaluation error: {e}", "score": 0.0}
    score = 0.0

    # Pattern 1: "Overall Score: X.X"
    matches = re.findall(r'Overall\s+Score:\s*([\d.]+)', eval_response)
    if matches:
        score = float(matches[-1])

    # Pattern 2: "Score: X.X" — use findall + last to avoid matching prompt text
    if score == 0.0:
        matches = re.findall(r'Score:\s*(?:\*\*?)?([\d.]+)(?:\s*\*\*?)?', eval_response, re.IGNORECASE)
        if matches:
            # Take the last match — it's most likely the LLM's actual answer
            score = float(matches[-1])
    return {"evaluation": eval_response[:5000], "score": score}

def analyze_skills(skill_filter: str = None):
    ANALYSIS_DIR.mkdir(exist_ok=True)
    skills = []
    for skill_dir in SKILL_DIRS:
        dir_path = Path(skill_dir)
        if not dir_path.exists():
            continue
        for skill_path in dir_path.rglob(SKILL_FILE):
            skill_meta = extract_skill_metadata(skill_path)
            if not skill_meta or not skill_meta.get("name"):
                continue
            if skill_filter and skill_meta.get("name", "").lower() != skill_filter.lower():
                continue
            skills.append(skill_meta)
    if not skills:
        print(f"No skills found")
        return []
    print(f"Found {len(skills)} skill(s)")
    server_info, server_process, using_fallback = None, None, False
    try:
        server_info = start_opencode_server()
        server_process = server_info['process']
    except RuntimeError as e:
        print(f"⚠ Server failed: {e}, using CLI")
        using_fallback = True
    results = []
    created_sessions = []
    try:
        for i, skill_meta in enumerate(skills, 1):
            skill_name = skill_meta.get("name", "")
            print(f"[{i}/{len(skills)}] {skill_name}")
            prompt = build_prompt(skill_meta)
            session_id = None
            if server_info and not using_fallback:
                response, exit_code, session_id = run_opencode_server(prompt, skill_name, server_info)
                if session_id:
                    created_sessions.append(session_id)
            else:
                response, exit_code = run_opencode_cli(prompt, skill_name)
            evaluation = evaluate_response(skill_name, response)
            if evaluation.get("score", 0.0) >= SCORE_THRESHOLD:
                print(f"  ✓ Score: {evaluation.get('score')}/1.0 - PASS")
                results.append({"skill": skill_name, "path": skill_meta["path"], "score": evaluation.get("score", 0.0), "exit_code": exit_code, "analysis_file": None})
            else:
                safe_name = re.sub(r'[^a-z0-9]', '_', skill_name.lower())
                analysis_file = ANALYSIS_DIR / f"{safe_name}.md"
                analysis_file.write_text(f"# Analysis: {skill_name}\nScore: {evaluation.get('score')}\n{evaluation.get('evaluation')}", encoding="utf-8")
                results.append({"skill": skill_name, "path": skill_meta["path"], "score": evaluation.get("score", 0.0), "exit_code": exit_code, "analysis_file": str(analysis_file)})
                print(f"  ⚠ Score: {evaluation.get('score')}/1.0 - {analysis_file}")
    finally:
        # Cleanup all created sessions
        if server_info and created_sessions:
            print(f"\n🧹 Cleaning up {len(created_sessions)} session(s)...")
            for sid in created_sessions:
                delete_session(server_info, sid)
        if server_process and server_process.poll() is None:
            server_process.terminate()
            server_process.wait(timeout=10)
    failed_count = sum(1 for r in results if r["analysis_file"])
    if failed_count:
        print(f"\n✅ Complete! {failed_count} failure(s) saved to {ANALYSIS_DIR}/")
    else:
        print(f"\n✅ Complete! All {len(results)} skill(s) passed.")
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill")
    args = parser.parse_args()
    analyze_skills(args.skill)

if __name__ == "__main__":
    main()
