use isideload::sideload::{application::{Application, SpecialApp}, cert_identity::CertificateIdentity};
use rsa::{pkcs8::DecodePrivateKey, RsaPrivateKey};
use x509_cert::{der::Decode, Certificate};

// Locally generated self-signed fixtures; never Apple credentials.
fn identity() -> CertificateIdentity {
    let dir = std::path::PathBuf::from(std::env::var("CERT_FIXTURE_DIR").unwrap());
    CertificateIdentity {
        machine_id: "local-fixture-password".into(), machine_name: "fixture".into(),
        private_key: RsaPrivateKey::from_pkcs8_der(&std::fs::read(dir.join("key.der")).unwrap()).unwrap(),
        certificate: Certificate::from_der(&std::fs::read(dir.join("cert.der")).unwrap()).unwrap(),
    }
}

fn app(label: &str) -> Application {
    let path = std::env::temp_dir().join(format!("container-fix-{}-{}.app", std::process::id(), label));
    std::fs::create_dir_all(&path).unwrap();
    let mut info = plist::Dictionary::new();
    info.insert("CFBundleIdentifier".into(), "com.kdt.livecontainer".into());
    info.insert("CFBundleName".into(), "LiveContainer".into());
    plist::to_file_xml(path.join("Info.plist"), &info).unwrap();
    Application::new(path).unwrap()
}

#[tokio::test]
async fn standalone_identity_is_exported_and_unlocks() {
    let mut application = app("handoff");
    assert_eq!(application.get_special_app(), Some(SpecialApp::LiveContainer));
    let identity = identity();
    application.apply_special_app_behavior(&Some(SpecialApp::LiveContainer), "group.fixture", &identity, None, None).await.unwrap();
    application.bundle.write_info().unwrap();
    let path = application.bundle.bundle_dir;
    let info = plist::Value::from_file(path.join("Info.plist")).unwrap();
    assert_eq!(info.as_dictionary().unwrap()["LCInstallerCertificatePassword"].as_string(), Some("local-fixture-password"));
    assert!(path.join("ALTCertificate.p12").is_file());
    // Save only this synthetic output for native Security.framework tests.
    std::fs::copy(path.join("ALTCertificate.p12"), std::path::PathBuf::from(std::env::var("CERT_FIXTURE_DIR").unwrap()).join("installer.p12")).unwrap();
}

#[tokio::test]
async fn empty_password_and_unrelated_apps_are_not_exported() {
    let mut application = app("empty");
    let mut identity = identity();
    identity.machine_id.clear();
    assert!(application.apply_special_app_behavior(&Some(SpecialApp::LiveContainer), "group.fixture", &identity, None, None).await.is_err());
    assert!(!application.bundle.bundle_dir.join("ALTCertificate.p12").exists());
    application.apply_special_app_behavior(&None, "group.fixture", &identity, None, None).await.unwrap();
    assert!(!application.bundle.bundle_dir.join("ALTCertificate.p12").exists());
}
