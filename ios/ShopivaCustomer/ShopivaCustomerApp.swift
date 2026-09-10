import SwiftUI
import WebKit

private let shopivaURL = URL(string: "https://shopiva-keny-ltd.onrender.com/")!

struct ShopivaWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .default()
        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.allowsBackForwardNavigationGestures = true
        webView.load(URLRequest(url: shopivaURL))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}
}

@main
struct ShopivaCustomerApp: App {
    var body: some Scene {
        WindowGroup {
            ShopivaWebView()
                .ignoresSafeArea(.container, edges: .bottom)
        }
    }
}
