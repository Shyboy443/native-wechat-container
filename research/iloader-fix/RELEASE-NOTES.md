An unsigned native container and an unofficial iLoader-based Windows installer with a standalone certificate handoff fix.

The Windows installer includes standalone LiveContainer in the existing certificate-export path. The matching iPhone app validates and imports the bundled signing identity. The user's development identity is created during local installation; public unsigned files contain no Apple credentials. Source: https://github.com/Shyboy443/native-wechat-container/tree/prototype/research/iloader-fix

The Apps screen now keeps Choose IPA File visible after the first import. Separately obtained WeChat and WhatsApp packages copied into the host Documents folder have direct import actions until imported. Every imported app now offers Add [app name] account profile, with separate app-group data and keychain storage. Compatibility and account login must be tested for each app. Remote push notifications are unavailable.

Download `AccountContainer-Windows-Setup.zip` on Windows and read `START-HERE.txt`. Apple Account authentication, a USB-connected trusted iPhone and Developer Mode are still required. Free signing must be renewed before expiry. This is not an iPhone Safari one-tap installer or TestFlight release.

Build and synthetic certificate test results are recorded in GitHub Actions. Version 0.3 was installed on an iPhone running iOS 27.3; certificate-import state and the imported WeChat bundle were verified over USB. The user reported a passing JIT-less diagnostic and confirmed that WeChat opens its login screen. Login, account separation and renewal remain unverified. The expanded import/profile controls and WhatsApp still require device tests. Third-party apps are separate dependencies and are not included in this release.

Based on LiveContainer (AGPL-3.0), iLoader and isideload (MIT). Official iLoader: https://iloader.app. This modified installer is not endorsed by upstream projects.
