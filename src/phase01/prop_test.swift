import CoreGraphics
import CoreText
import Foundation

let fps = 30
let frameCount = 90
let pinchContactFrame = 18
let grabFrame = 21
let releaseFrame = 59
let landingFrame = 63
let sampleRate = 48_000
let width = 540
let height = 960
let stageWidth: CGFloat = 450
let floor: CGFloat = 620
let baseOffset: CGFloat = 54
let restingX: CGFloat = 185

struct Pose {
    let frame: Int
    let x: CGFloat
    let y: CGFloat
    let angle: CGFloat
    let closure: CGFloat
}

let handKeys = [
    Pose(frame: 0, x: 487, y: 625, angle: 0.25, closure: 0),
    Pose(frame: 8, x: 364, y: 586, angle: 0.18, closure: 0),
    Pose(frame: 15, x: 221, y: 554, angle: 0.06, closure: 0),
    Pose(frame: grabFrame, x: restingX, y: floor - baseOffset, angle: 0, closure: 1),
    Pose(frame: 25, x: restingX, y: floor - baseOffset, angle: 0, closure: 1),
    Pose(frame: 34, x: 197, y: 490, angle: -0.10, closure: 1),
    Pose(frame: 43, x: 214, y: 446, angle: -0.16, closure: 1),
    Pose(frame: 49, x: 224, y: 460, angle: 0.11, closure: 1),
    Pose(frame: 55, x: 195, y: 533, angle: 0.08, closure: 1),
    Pose(frame: releaseFrame, x: restingX, y: floor - baseOffset - 12, angle: 0, closure: 1),
    Pose(frame: 60, x: 196, y: 553, angle: -0.02, closure: 0.32),
    Pose(frame: 63, x: 219, y: 548, angle: -0.08, closure: 0.02),
    Pose(frame: 73, x: 335, y: 560, angle: 0.03, closure: 0),
    Pose(frame: 85, x: 500, y: 610, angle: 0.2, closure: 0),
]

func mix(_ first: CGFloat, _ second: CGFloat, _ weight: CGFloat) -> CGFloat {
    first + (second - first) * weight
}

func handPose(at frame: Int) -> Pose {
    guard let index = handKeys.firstIndex(where: { $0.frame > frame }) else {
        return handKeys.last!
    }
    let first = handKeys[index - 1]
    let second = handKeys[index]
    let previous = handKeys[max(index - 2, 0)]
    let next = handKeys[min(index + 1, handKeys.count - 1)]
    let span = CGFloat(second.frame - first.frame)
    let t = CGFloat(frame - first.frame) / span
    let eased = t * t * (3 - 2 * t)

    func position(_ field: KeyPath<Pose, CGFloat>) -> CGFloat {
        let start = first[keyPath: field]
        let end = second[keyPath: field]
        let startTangent = (end - previous[keyPath: field]) * span / CGFloat(second.frame - previous.frame)
        let endTangent = (next[keyPath: field] - start) * span / CGFloat(next.frame - first.frame)
        let curve = mix(start, end, eased)
            + t * (1 - t) * ((1 - t) * startTangent - t * endTangent)
        return min(max(start, end), max(min(start, end), curve))
    }

    return Pose(frame: frame, x: position(\.x), y: position(\.y),
                angle: position(\.angle), closure: mix(first.closure, second.closure, eased))
}

func lipstickPose(at frame: Int, hand: Pose) -> Pose {
    if (grabFrame...releaseFrame).contains(frame) {
        return hand
    }
    let elapsed = CGFloat(frame - releaseFrame)
    let fallTime = CGFloat(landingFrame - releaseFrame)
    if frame > releaseFrame, frame < landingFrame {
        let drop = 12 * pow(elapsed / fallTime, 2)
        return Pose(frame: frame, x: restingX, y: floor - baseOffset - 12 + drop, angle: 0, closure: 0)
    }
    let rebound = max(0, 1 - abs(CGFloat(frame - landingFrame) - 2) / 2) * 1.4
    return Pose(frame: frame, x: restingX, y: floor - baseOffset - rebound, angle: 0, closure: 0)
}

let colorSpace = CGColorSpaceCreateDeviceRGB()
let outline: UInt32 = 0x622C3A
let skin: UInt32 = 0xF2AE95
let shadowSkin: UInt32 = 0xCC7B72
let warmLight: UInt32 = 0xFFD1B6

func color(_ rgb: UInt32, _ alpha: CGFloat = 1) -> CGColor {
    CGColor(red: CGFloat((rgb >> 16) & 255) / 255,
            green: CGFloat((rgb >> 8) & 255) / 255,
            blue: CGFloat(rgb & 255) / 255, alpha: alpha)
}

func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: x, y: y) }

func shape(_ context: CGContext, fill: UInt32, edge: UInt32? = nil, weight: CGFloat = 1.8,
           _ draw: (CGMutablePath) -> Void) {
    let path = CGMutablePath()
    draw(path)
    path.closeSubpath()
    context.addPath(path)
    context.setFillColor(color(fill))
    if let edge {
        context.setStrokeColor(color(edge))
        context.setLineWidth(weight)
        context.setLineJoin(.round)
        context.drawPath(using: .fillStroke)
    } else {
        context.fillPath()
    }
}

func gradient(_ context: CGContext, from: UInt32, to: UInt32, start: CGPoint, end: CGPoint) {
    let colors = [color(from), color(to)] as CFArray
    context.drawLinearGradient(CGGradient(colorsSpace: colorSpace, colors: colors, locations: nil)!,
                               start: start, end: end, options: [.drawsBeforeStartLocation, .drawsAfterEndLocation])
}

func contactShadow(_ context: CGContext, x: CGFloat, y: CGFloat, radius: CGFloat,
                   depth: CGFloat, opacity: CGFloat) {
    let colors = [color(0x743243, opacity), color(0x743243, 0)] as CFArray
    let gradient = CGGradient(colorsSpace: colorSpace, colors: colors, locations: [0, 1])!
    context.saveGState()
    context.translateBy(x: x, y: y)
    context.scaleBy(x: 1, y: depth / radius)
    context.drawRadialGradient(gradient, startCenter: .zero, startRadius: 0,
                               endCenter: .zero, endRadius: radius, options: [])
    context.restoreGState()
}

func caption(_ context: CGContext, _ text: String, at position: CGPoint, font: String,
             size: CGFloat, ink: UInt32) {
    let line = CTLineCreateWithAttributedString(NSAttributedString(string: text, attributes: [
        NSAttributedString.Key(kCTFontAttributeName as String): CTFontCreateWithName(font as CFString, size, nil),
        NSAttributedString.Key(kCTForegroundColorAttributeName as String): color(ink),
    ]))
    context.saveGState()
    context.translateBy(x: position.x, y: position.y)
    context.scaleBy(x: 1, y: -1)
    context.textPosition = .zero
    CTLineDraw(line, context)
    context.restoreGState()
}

func stage(_ context: CGContext) {
    gradient(context, from: 0x48263B, to: 0x997284, start: p(40, 25), end: p(417, 700))
    context.saveGState()
    context.clip(to: CGRect(x: 0, y: 526, width: stageWidth, height: 168))
    gradient(context, from: 0xF6D8BF, to: 0xDBA797, start: p(0, 526), end: p(286, 696))
    context.restoreGState()
    context.setFillColor(color(0xD6A278))
    context.fill(CGRect(x: 0, y: 691, width: stageWidth, height: 3))
    context.setFillColor(color(0x3F2435))
    context.fill(CGRect(x: 0, y: 694, width: stageWidth, height: 106))
    context.setFillColor(color(0xC69869))
    context.fill(CGRect(x: 41, y: 113, width: 38, height: 1))
    caption(context, "Ruj teması", at: p(39, 162), font: "Georgia", size: 42, ink: 0xFFF1E1)
    caption(context, "Mekanik prova", at: p(42, 192), font: "HelveticaNeue-Medium", size: 16, ink: 0xEDC4AC)
}

func backHand(_ context: CGContext, closure: CGFloat) {
    let indexTip = mix(-24, -12, closure)
    let indexHeight = mix(-31, -5, closure)
    shape(context, fill: 0x7F294A, edge: outline) { path in
        path.move(to: p(99, 18))
        path.addQuadCurve(to: p(272, 63), control: p(182, 35))
        path.addLine(to: p(288, 131))
        path.addQuadCurve(to: p(92, 63), control: p(190, 101))
        path.addQuadCurve(to: p(99, 18), control: p(84, 38))
    }
    shape(context, fill: 0xBD8265, edge: outline) { path in
        path.move(to: p(104, 20))
        path.addQuadCurve(to: p(95, 64), control: p(95, 40))
        path.addLine(to: p(107, 68))
        path.addQuadCurve(to: p(115, 22), control: p(105, 49))
    }
    shape(context, fill: shadowSkin, edge: outline) { path in
        path.move(to: p(50, 10))
        path.addCurve(to: p(-8, 19), control1: p(29, 4), control2: p(6, 12))
        path.addCurve(to: p(2, 33), control1: p(-16, 24), control2: p(-10, 34))
        path.addQuadCurve(to: p(54, 30), control: p(28, 28))
    }
    shape(context, fill: 0xE99983, edge: outline) { path in
        path.move(to: p(55, 2))
        path.addCurve(to: p(indexTip + 4, indexHeight + 11),
                      control1: p(21, -15), control2: p(indexTip + 16, indexHeight + 2))
        path.addCurve(to: p(indexTip + 15, indexHeight + 23),
                      control1: p(indexTip - 4, indexHeight + 18), control2: p(indexTip + 1, indexHeight + 25))
        path.addQuadCurve(to: p(63, 19), control: p(34, 12))
    }
    shape(context, fill: skin, edge: outline) { path in
        path.move(to: p(102, 21))
        path.addCurve(to: p(47, -16), control1: p(73, 11), control2: p(72, -14))
        path.addCurve(to: p(indexTip, indexHeight),
                      control1: p(17, -25), control2: p(indexTip + 13, indexHeight - 11))
        path.addCurve(to: p(indexTip + 8, indexHeight + 13),
                      control1: p(indexTip - 9, indexHeight + 8), control2: p(indexTip - 4, indexHeight + 17))
        path.addQuadCurve(to: p(38, -1), control: p(21, -14))
        path.addCurve(to: p(53, 34), control1: p(31, 10), control2: p(49, 11))
        path.addQuadCurve(to: p(94, 59), control: p(61, 53))
        path.addQuadCurve(to: p(102, 21), control: p(88, 40))
    }
}

func frontThumb(_ context: CGContext, closure: CGFloat) {
    let thumbX = mix(18, -12, closure)
    let thumbY = mix(42, 7, closure)
    shape(context, fill: skin, edge: outline) { path in
        path.move(to: p(69, 26))
        path.addCurve(to: p(thumbX + 17, thumbY - 5), control1: p(59, 17), control2: p(thumbX + 35, thumbY - 10))
        path.addCurve(to: p(thumbX, thumbY), control1: p(thumbX + 5, thumbY - 4), control2: p(thumbX + 2, thumbY - 4))
        path.addCurve(to: p(thumbX + 10, thumbY + 13), control1: p(thumbX - 6, thumbY + 6), control2: p(thumbX, thumbY + 15))
        path.addQuadCurve(to: p(71, 44), control: p(51, thumbY + 16))
        path.addQuadCurve(to: p(69, 26), control: p(78, 38))
    }
    shape(context, fill: 0xB74D65, edge: outline, weight: 1) { path in
        path.move(to: p(thumbX + 2, thumbY + 2))
        path.addCurve(to: p(thumbX + 14, thumbY + 2), control1: p(thumbX + 4, thumbY - 2), control2: p(thumbX + 12, thumbY - 2))
        path.addQuadCurve(to: p(thumbX + 4, thumbY + 9), control: p(thumbX + 16, thumbY + 11))
        path.addQuadCurve(to: p(thumbX + 2, thumbY + 2), control: p(thumbX, thumbY + 7))
    }
}

func lipstick(_ context: CGContext) {
    shape(context, fill: 0xA72F53, edge: outline) { path in
        path.move(to: p(-10, -17))
        path.addLine(to: p(-10, -42))
        path.addQuadCurve(to: p(7, -57), control: p(-4, -54))
        path.addQuadCurve(to: p(10, -52), control: p(10, -57))
        path.addLine(to: p(10, -17))
    }
    shape(context, fill: 0xD76682) { path in
        path.move(to: p(-8, -43))
        path.addQuadCurve(to: p(7, -55), control: p(-4, -51))
        path.addQuadCurve(to: p(-8, -37), control: p(7, -48))
    }
    shape(context, fill: 0xE6BD7A, edge: outline) { path in
        path.move(to: p(-12, -19))
        path.addQuadCurve(to: p(12, -19), control: p(0, -16))
        path.addLine(to: p(12, 8))
        path.addLine(to: p(-12, 8))
    }
    context.setFillColor(color(0xFFF0B1, 0.65))
    context.fill(CGRect(x: -7, y: -17, width: 4, height: 21))
    shape(context, fill: 0x713550, edge: outline) { path in
        path.move(to: p(-15, 4))
        path.addQuadCurve(to: p(15, 4), control: p(0, 8))
        path.addLine(to: p(15, 49))
        path.addQuadCurve(to: p(-15, 49), control: p(0, 58))
    }
    shape(context, fill: 0x9C5670) { path in
        path.move(to: p(-11, 9))
        path.addLine(to: p(-5, 10))
        path.addLine(to: p(-5, 49))
        path.addLine(to: p(-11, 47))
    }
}

func layer(_ context: CGContext, at pose: Pose, _ draw: () -> Void) {
    context.saveGState()
    context.translateBy(x: pose.x, y: pose.y)
    context.rotate(by: pose.angle)
    draw()
    context.restoreGState()
}

func drawFrame(_ frame: Int, context: CGContext) {
    let hand = handPose(at: frame)
    let prop = lipstickPose(at: frame, hand: hand)
    let propHeight = max(0, floor - prop.y - baseOffset)
    let handHeight = max(0, floor - hand.y - 30)

    stage(context)
    context.saveGState()
    context.translateBy(x: restingX, y: floor)
    context.scaleBy(x: 1.22, y: 1.22)
    context.translateBy(x: -restingX, y: -floor)
    contactShadow(context, x: hand.x + 95, y: 642, radius: 118 + handHeight * 0.22,
                  depth: 17 + handHeight * 0.12, opacity: 0.22 / (1 + handHeight / 95))
    contactShadow(context, x: prop.x - propHeight * 0.16 + 3, y: floor + 3,
                  radius: 27 + propHeight * 0.26, depth: 8 + propHeight * 0.08,
                  opacity: 0.50 / (1 + propHeight / 37))
    layer(context, at: hand) { backHand(context, closure: hand.closure) }
    layer(context, at: prop) { lipstick(context) }
    layer(context, at: hand) { frontThumb(context, closure: hand.closure) }
    context.restoreGState()
}

func appendLittleEndian<T: FixedWidthInteger>(_ number: T, to data: inout Data) {
    var value = number.littleEndian
    withUnsafeBytes(of: &value) { data.append(contentsOf: $0) }
}

func writeFoley(to url: URL) throws {
    let sampleCount = frameCount * sampleRate / fps
    let landmarks = [(pinchContactFrame, 3_200.0, 0.30), (landingFrame, 1_730.0, 0.37)]
    var samples = [Double](repeating: 0, count: sampleCount)
    for (frame, frequency, amplitude) in landmarks {
        let start = frame * sampleRate / fps
        for offset in 0..<2_400 {
            let t = Double(offset) / Double(sampleRate)
            let bright = cos(2 * .pi * frequency * t) * exp(-t * 210)
            let body = cos(2 * .pi * 360 * t) * exp(-t * 140)
            samples[start + offset] += amplitude * (bright * 0.78 + body * 0.22)
        }
    }
    var wav = Data("RIFF".utf8)
    appendLittleEndian(UInt32(36 + sampleCount * 2), to: &wav)
    wav.append(contentsOf: "WAVEfmt ".utf8)
    appendLittleEndian(UInt32(16), to: &wav)
    appendLittleEndian(UInt16(1), to: &wav)
    appendLittleEndian(UInt16(1), to: &wav)
    appendLittleEndian(UInt32(sampleRate), to: &wav)
    appendLittleEndian(UInt32(sampleRate * 2), to: &wav)
    appendLittleEndian(UInt16(2), to: &wav)
    appendLittleEndian(UInt16(16), to: &wav)
    wav.append(contentsOf: "data".utf8)
    appendLittleEndian(UInt32(sampleCount * 2), to: &wav)
    for sample in samples {
        appendLittleEndian(Int16(sample * 32_767), to: &wav)
    }
    try wav.write(to: url)
}

enum RenderError: Error {
    case cannotCreateContext
    case encodeFailed(Int32)
}

func render(to output: URL) throws {
    let files = FileManager.default
    let temporary = files.temporaryDirectory.appendingPathComponent("lalin-prop-\(UUID().uuidString)")
    try files.createDirectory(at: temporary, withIntermediateDirectories: false)
    defer { try? files.removeItem(at: temporary) }
    try files.createDirectory(at: output.deletingLastPathComponent(), withIntermediateDirectories: true)
    let wav = temporary.appendingPathComponent("clicks.wav")
    let movie = temporary.appendingPathComponent("proof.mp4")
    try writeFoley(to: wav)

    let bytesPerRow = width * 4
    let bitmapInfo = CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
    guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
                                  bytesPerRow: bytesPerRow, space: colorSpace, bitmapInfo: bitmapInfo),
          let pixels = context.data else { throw RenderError.cannotCreateContext }
    context.translateBy(x: 0, y: CGFloat(height))
    let scale = CGFloat(width) / stageWidth
    context.scaleBy(x: scale, y: -scale)

    let input = Pipe()
    let encoder = Process()
    encoder.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    encoder.arguments = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-filter_threads", "1",
        "-f", "rawvideo", "-pixel_format", "bgra", "-video_size", "\(width)x\(height)",
        "-framerate", "\(fps)", "-i", "pipe:0", "-i", wav.path,
        "-c:v", "libx264", "-threads:v", "1", "-preset", "veryfast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", movie.path,
    ]
    encoder.standardInput = input
    try encoder.run()
    do {
        for frame in 0..<frameCount {
            drawFrame(frame, context: context)
            let bytes = Data(bytesNoCopy: pixels, count: bytesPerRow * height, deallocator: .none)
            try input.fileHandleForWriting.write(contentsOf: bytes)
        }
        try input.fileHandleForWriting.close()
    } catch {
        try? input.fileHandleForWriting.close()
        encoder.waitUntilExit()
        throw error
    }
    encoder.waitUntilExit()
    guard encoder.terminationStatus == 0 else { throw RenderError.encodeFailed(encoder.terminationStatus) }
    if files.fileExists(atPath: output.path) {
        _ = try files.replaceItemAt(output, withItemAt: movie)
    } else {
        try files.moveItem(at: movie, to: output)
    }
}

let outputPath = CommandLine.arguments.dropFirst().first ?? "outputs/phase01/lalin_prop_test.mp4"
try render(to: URL(fileURLWithPath: outputPath))
