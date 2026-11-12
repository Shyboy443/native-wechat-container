# AccountContainer Installer

Unofficial iLoader 2.4.1 build with a targeted standalone LiveContainer certificate handoff fix.
Official iLoader: https://iloader.app and https://github.com/nab138/iloader.
Neither upstream project endorses this modification. iLoader/isideload source is MIT licensed.

The patch includes standalone LiveContainer in isideload's existing PKCS#12 export path,
and passes its archive password to our matching native certificate importer.
The certificate is generated during the user's local signing session and only embedded in
that device-specific signed installation. Public unsigned packages contain no signing key.
Keep signed copies private: the installed app bundle contains the development identity.

The native importer checks that PKCS#12 contains an identity and that its team matches
the installed host. It imports once per bundled certificate and updates after reinstall.
It preserves an explicit certificate removal until a new installer identity is supplied.

This removes the SideStore certificate-transfer step. It does not establish WeChat runtime compatibility.
Free provisioning still expires, normally after seven days; reconnect and reinstall the same
host with the same Apple Account before expiry. Keep the app installed to preserve its data.
Do not uninstall as a renewal step. Recheck both account profiles after renewal.

Use Import IPA to install the matching NativeContainer-unsigned.ipa. Do not select
Install SideStore or the LiveContainer+SideStore bundle. Sign in to Apple yourself.
The app still needs Apple's Windows device drivers and the phone's Developer Mode/trust setup.

Verification: the workflow tests PKCS#12 creation with a disposable self-signed fixture,
then builds the Windows application. Native Security.framework validation is tested separately.
Successful compilation is not proof of iPhone installation, login or account switching.
