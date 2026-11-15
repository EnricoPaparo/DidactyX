import SwiftUI

enum Theme {
    static let background = Color(red: 0.043, green: 0.059, blue: 0.078)
    static let panel = Color(red: 0.063, green: 0.086, blue: 0.110)
    static let raised = Color(red: 0.082, green: 0.110, blue: 0.137)
    static let border = Color(red: 0.145, green: 0.192, blue: 0.224)
    static let cyan = Color(red: 0.36, green: 0.87, blue: 0.91)
    static let secondary = Color(red: 0.56, green: 0.64, blue: 0.69)
    static let text = Color(red: 0.91, green: 0.94, blue: 0.95)
    static let warning = Color(red: 1, green: 0.71, blue: 0.43)
    static func mono(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .monospaced)
    }
}

struct PrimaryButton: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 13, weight: .semibold))
            .foregroundStyle(Theme.background)
            .padding(.horizontal, 17).padding(.vertical, 11)
            .background(Theme.cyan.opacity(configuration.isPressed ? 0.75 : 1), in: RoundedRectangle(cornerRadius: 8))
    }
}

struct QuietButton: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: 13, weight: .medium))
            .foregroundStyle(Theme.text)
            .padding(.horizontal, 13).padding(.vertical, 10)
            .background(configuration.isPressed ? Theme.raised : Theme.panel, in: RoundedRectangle(cornerRadius: 8))
            .overlay(RoundedRectangle(cornerRadius: 8).stroke(Theme.border, lineWidth: 1))
    }
}

struct Brand: View {
    var compact = false
    var body: some View {
        HStack(spacing: 12) {
            Text(">_")
                .font(Theme.mono(compact ? 15 : 19, .semibold))
                .foregroundStyle(Theme.cyan)
                .frame(width: compact ? 34 : 42, height: compact ? 34 : 42)
                .background(Theme.cyan.opacity(0.075), in: RoundedRectangle(cornerRadius: 9))
                .overlay(RoundedRectangle(cornerRadius: 9).stroke(Theme.cyan.opacity(0.2)))
            Text("DidactyX").font(Theme.mono(compact ? 19 : 25, .medium)).tracking(-0.8)
        }
        .foregroundStyle(Theme.text)
        .accessibilityElement(children: .combine)
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
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            FieldLabel(text: label)
            TextField(placeholder, text: $text, axis: multiline ? .vertical : .horizontal)
                .lineLimit(multiline ? 3...6 : 1...1)
                .textFieldStyle(.plain)
                .font(.system(size: 14))
                .padding(12)
                .background(Theme.panel, in: RoundedRectangle(cornerRadius: 7))
                .overlay(RoundedRectangle(cornerRadius: 7).stroke(Theme.border))
                .accessibilityLabel(label)
        }
    }
}
