An unsigned native container and an unofficial iLoader-based Windows installer with a standalone certificate handoff fix.

The Windows installer includes standalone LiveContainer in the existing certificate-export path. The matching iPhone app validates and imports the bundled signing identity. The user's development identity is created during local installation; public unsigned files contain no Apple credentials. Source: https://github.com/Shyboy443/native-wechat-container/tree/prototype/research/iloader-fix

The empty Apps screen now includes a direct Import WeChat action when the separately obtained package has been copied into the host Documents folder. Otherwise it offers Choose IPA File. The existing + menu uses Install IPA File.

Download `AccountContainer-Windows-Setup.zip` on Windows and read `START-HERE.txt`. Apple Account authentication, a USB-connected trusted iPhone and Developer Mode are still required. Free signing must be renewed before expiry. This is not an iPhone Safari one-tap installer or TestFlight release.

Build and synthetic certificate test results are recorded in GitHub Actions. The preceding certificate-fix build was installed on an iPhone running iOS 27.3; certificate-import state was verified over USB, and the user reported a passing JIT-less diagnostic. The new import action still needs its device test. WeChat launch, login, session isolation and renewal remain unverified. WeChat is a separate dependency and is not included in this release.

Based on LiveContainer (AGPL-3.0), iLoader and isideload (MIT). Official iLoader: https://iloader.app. This modified installer is not endorsed by upstream projects.
