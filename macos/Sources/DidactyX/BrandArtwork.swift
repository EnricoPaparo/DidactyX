import AppKit

/// Shared vector artwork for the SwiftUI identity, SVG masters and macOS icon.
enum BrandArtwork {
    static let mint: UInt32 = 0x57F2CE
    static let violet: UInt32 = 0xAB92FF
    static let pink: UInt32 = 0xF47ACB
    static let ink: UInt32 = 0x0D0B14

    // Four folded page facets form an X around a small point of connection.
    // Coordinates use a 100 × 100 canvas, with the origin at the top left.
    static let facets: [[CGPoint]] = [
        [.init(x: 17, y: 18), .init(x: 37, y: 24), .init(x: 47, y: 40), .init(x: 40, y: 49), .init(x: 27, y: 34), .init(x: 17, y: 31)],
        [.init(x: 83, y: 18), .init(x: 63, y: 24), .init(x: 53, y: 40), .init(x: 60, y: 49), .init(x: 73, y: 34), .init(x: 83, y: 31)],
        [.init(x: 40, y: 51), .init(x: 47, y: 60), .init(x: 37, y: 76), .init(x: 17, y: 82), .init(x: 17, y: 69), .init(x: 27, y: 66)],
        [.init(x: 60, y: 51), .init(x: 53, y: 60), .init(x: 63, y: 76), .init(x: 83, y: 82), .init(x: 83, y: 69), .init(x: 73, y: 66)]
    ]
    static let center: [CGPoint] = [.init(x: 50, y: 44), .init(x: 56, y: 50), .init(x: 50, y: 56), .init(x: 44, y: 50)]

    static func path(_ points: [CGPoint]) -> CGPath {
        let path = CGMutablePath()
        path.addLines(between: points)
        path.closeSubpath()
        return path
    }

    static func color(_ hex: UInt32, alpha: CGFloat = 1) -> NSColor {
        NSColor(srgbRed: CGFloat((hex >> 16) & 255) / 255,
                green: CGFloat((hex >> 8) & 255) / 255,
                blue: CGFloat(hex & 255) / 255, alpha: alpha)
    }

    static func draw(in context: CGContext, size: CGFloat, tile: Bool) {
        context.saveGState()
        context.scaleBy(x: size / 100, y: size / 100)
        let space = CGColorSpace(name: CGColorSpace.sRGB)!
        func fill(_ path: CGPath, _ colors: [UInt32], from: CGPoint, to: CGPoint) {
            context.saveGState()
            context.addPath(path); context.clip()
            let gradient = CGGradient(colorsSpace: space, colors: colors.map { color($0).cgColor } as CFArray, locations: nil)!
            context.drawLinearGradient(gradient, start: from, end: to, options: [.drawsBeforeStartLocation, .drawsAfterEndLocation])
            context.restoreGState()
        }
        if tile {
            let shape = CGPath(roundedRect: CGRect(x: 6, y: 6, width: 88, height: 88), cornerWidth: 20, cornerHeight: 20, transform: nil)
            context.setShadow(offset: CGSize(width: 0, height: 2), blur: 3, color: color(0x000000, alpha: 0.3).cgColor)
            fill(shape, [0x241B36, ink], from: .zero, to: CGPoint(x: 75, y: 100))
            context.setShadow(offset: .zero, blur: 0, color: nil)
            context.addPath(shape); context.setLineWidth(0.65)
            context.setStrokeColor(color(violet, alpha: 0.30).cgColor); context.strokePath()
        }
        for (index, points) in facets.enumerated() {
            let palette: [UInt32] = index == 0 || index == 3 ? [0xA2FFE5, mint, 0x27B6BB] : [violet, pink]
            fill(path(points), palette, from: CGPoint(x: 20, y: 15), to: CGPoint(x: 80, y: 85))
        }
        context.addPath(path(center)); context.setFillColor(color(0xF4EEFF).cgColor); context.fillPath()
        context.restoreGState()
    }

    static func svg(tile: Bool) -> String {
        let paths = facets.enumerated().map { index, points in
            let coordinates = points.map { "\(Int($0.x)),\(Int($0.y))" }.joined(separator: " ")
            return "<polygon points=\"\(coordinates)\" fill=\"url(#\(index == 0 || index == 3 ? "mint" : "violet"))\"/>"
        }.joined(separator: "\n")
        return """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="DidactyX">
        <defs>
          <linearGradient id="mint" x1="20" y1="15" x2="80" y2="85" gradientUnits="userSpaceOnUse"><stop stop-color="#A2FFE5"/><stop offset=".5" stop-color="#57F2CE"/><stop offset="1" stop-color="#27B6BB"/></linearGradient>
          <linearGradient id="violet" x1="20" y1="15" x2="80" y2="85" gradientUnits="userSpaceOnUse"><stop stop-color="#AB92FF"/><stop offset="1" stop-color="#F47ACB"/></linearGradient>
          <linearGradient id="tile" x2="75%" y2="100%"><stop stop-color="#241B36"/><stop offset="1" stop-color="#0D0B14"/></linearGradient>
        </defs>
        \(tile ? "<rect x=\"6\" y=\"6\" width=\"88\" height=\"88\" rx=\"20\" fill=\"url(#tile)\" stroke=\"#AB92FF\" stroke-opacity=\".3\" stroke-width=\".65\"/>" : "")
        \(paths)
        <path d="M50 44 56 50 50 56 44 50Z" fill="#F4EEFF"/>
        </svg>
        """
    }
}
