An unsigned native container and an unofficial iLoader-based Windows installer with a standalone certificate handoff fix.

The Windows installer includes standalone LiveContainer in the existing certificate-export path. The matching iPhone app validates and imports the bundled signing identity. The user's development identity is created during local installation; public unsigned files contain no Apple credentials. Source: https://github.com/Shyboy443/native-wechat-container/tree/prototype/research/iloader-fix

Download `AccountContainer-Windows-Setup.zip` on Windows and read `START-HERE.txt`. Apple Account authentication, a USB-connected trusted iPhone and Developer Mode are still required. Free signing must be renewed before expiry. This is not an iPhone Safari one-tap installer or TestFlight release.

Build and synthetic certificate test results are recorded in GitHub Actions. Successful compilation does not establish physical iPhone installation, WeChat launch, login, session isolation or renewal. WeChat is a separate dependency and is not included in this release.

Based on LiveContainer (AGPL-3.0), iLoader and isideload (MIT). Official iLoader: https://iloader.app. This modified installer is not endorsed by upstream projects.
