import SwiftUI

enum Theme {
    static let background = Color(BrandArtwork.color(BrandArtwork.ink))
    static let panel = Color(BrandArtwork.color(0x171321))
    static let raised = Color(BrandArtwork.color(0x231C31))
    static let border = Color(BrandArtwork.color(0x393047))
    static let cyan = Color(BrandArtwork.color(BrandArtwork.mint))
    static let violet = Color(BrandArtwork.color(BrandArtwork.violet))
    static let pink = Color(BrandArtwork.color(BrandArtwork.pink))
    static let secondary = Color(BrandArtwork.color(0xABA2BC))
    static let text = Color(BrandArtwork.color(0xF4F0FB))
    static let warning = Color(BrandArtwork.color(0xFFD08A))
    static let spectrum = LinearGradient(colors: [cyan, violet, pink], startPoint: .leading, endPoint: .trailing)
    static func mono(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .monospaced)
    }
}

struct AmbientBackground: View {
    var body: some View {
        GeometryReader { geometry in
            ZStack {
                Theme.background
                RadialGradient(colors: [Theme.violet.opacity(0.10), .clear], center: .topTrailing,
                               startRadius: 0, endRadius: max(geometry.size.width * 0.7, 500))
                RadialGradient(colors: [Theme.cyan.opacity(0.045), .clear], center: .bottomLeading,
                               startRadius: 0, endRadius: max(geometry.size.width * 0.6, 400))
            }
        }.allowsHitTesting(false).accessibilityHidden(true)
    }
}

struct BrandSymbol: View {
    var body: some View {
        Canvas { context, size in
            context.withCGContext { cg in
                BrandArtwork.draw(in: cg, size: min(size.width, size.height), tile: false)
            }
        }.accessibilityHidden(true)
    }
}

struct PrimaryButton: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 13, weight: .semibold))
            .foregroundStyle(Theme.background)
            .padding(.horizontal, 17).padding(.vertical, 11)
            .background(LinearGradient(colors: [Theme.cyan, Color(BrandArtwork.color(0x76E3EF))],
                                       startPoint: .topLeading, endPoint: .bottomTrailing), in: RoundedRectangle(cornerRadius: 8))
            .overlay(RoundedRectangle(cornerRadius: 8).stroke(.white.opacity(0.18), lineWidth: 1))
            .shadow(color: Theme.cyan.opacity(isEnabled ? 0.13 : 0), radius: 12, y: 3)
            .brightness(configuration.isPressed ? -0.10 : 0)
            .opacity(isEnabled ? 1 : 0.4)
    }
}

struct QuietButton: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 13, weight: .medium))
            .foregroundStyle(Theme.text)
            .padding(.horizontal, 13).padding(.vertical, 10)
            .background(configuration.isPressed ? Theme.raised : Theme.panel, in: RoundedRectangle(cornerRadius: 8))
            .overlay(RoundedRectangle(cornerRadius: 8).stroke(configuration.isPressed ? Theme.violet.opacity(0.7) : Theme.border, lineWidth: 1))
            .opacity(isEnabled ? 1 : 0.4)
    }
}

struct Brand: View {
    var compact = false
    var body: some View {
        HStack(spacing: 12) {
            BrandSymbol()
                .frame(width: compact ? 36 : 48, height: compact ? 36 : 48)
            (Text("Didacty").foregroundStyle(Theme.text) + Text("X").foregroundStyle(Theme.violet))
                .font(.system(size: compact ? 23 : 31, weight: .semibold, design: .rounded)).tracking(-1.1)
        }
        .foregroundStyle(Theme.text)
        .accessibilityElement(children: .ignore).accessibilityLabel("DidactyX")
    }
}

struct FieldLabel: View {
    let text: String
    var body: some View {
        Text(text.uppercased()).font(Theme.mono(10, .medium)).tracking(1.3).foregroundStyle(Theme.secondary)
    }
}

struct InputField: View {
    let label: String
    let placeholder: String
    @Binding var text: String
    var multiline = false
    @FocusState private var focused: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            FieldLabel(text: label)
            TextField(placeholder, text: $text, axis: multiline ? .vertical : .horizontal)
                .lineLimit(multiline ? 3...6 : 1...1)
                .textFieldStyle(.plain)
                .focused($focused)
                .font(.system(size: 14))
                .padding(12)
                .background(Theme.panel, in: RoundedRectangle(cornerRadius: 7))
                .overlay(RoundedRectangle(cornerRadius: 7).stroke(focused ? Theme.violet.opacity(0.8) : Theme.border))
                .accessibilityLabel(label)
        }
    }
}
