> Loaded on demand from SKILL.md when the agent needs the complete web-ext command reference.

# web-ext CLI Reference

## Installation

```bash
npm install -g web-ext
```

## Run Command (Development)

```bash
web-ext run                                    # Default Firefox
web-ext run --firefox-path /path/to/firefox    # Specific Firefox
web-ext run --target firefox-android           # Android
web-ext run --profile-create-new               # Clean profile
web-ext run --start-url https://example.com    # Start URL
web-ext run --verbose                          # Verbose output
web-ext run --no-reload                        # Disable auto-reload
web-ext run --pref extensions.webextensions.debug=true
```

## Lint Command (Validation)

```bash
web-ext lint                   # Validate manifest and code
web-ext lint --warnings-as-errors
web-ext lint --self-hosted     # Skip AMO-specific checks
web-ext lint --verbose
```

## Build Command (Create Artifact)

```bash
web-ext build                  # Create .zip in web-ext-artifacts/
web-ext build --source-dir ./src
web-ext build --artifacts-dir ./dist
web-ext build --overwrite-dest
```

## Sign Command (AMO Submission)

```bash
web-ext sign --api-key $KEY --api-secret $SECRET
web-ext sign --channel listed      # Public on AMO
web-ext sign --channel unlisted    # Direct download
web-ext sign --amo-base-url https://addons.mozilla.org
```

## Other Commands

```bash
web-ext docs                   # Open documentation
web-ext dump-config            # Show configuration
web-ext sign --channel unlisted --force-sign
```

## Configuration File (.web-ext-config.js)

```javascript
module.exports = {
  sourceDir: './src',
  artifactsDir: './dist',

  run: {
    firefox: '/Applications/Firefox.app/Contents/MacOS/firefox',
    startUrl: 'https://example.com',
    pref: ['extensions.webextensions.debug=true']
  },

  build: {
    overwriteDest: true
  },

  sign: {
    apiKey: process.env.AMO_API_KEY,
    apiSecret: process.env.AMO_API_SECRET,
    channel: 'listed'
  }
};
```

## Environment Variables

```bash
WEB_EXT_API_KEY=your_key
WEB_EXT_API_SECRET=your_secret
WEB_EXT_SOURCE_DIR=./src
WEB_EXT_ARTIFACTS_DIR=./dist
WEB_EXT_FIREFOX=/path/to/firefox
```
