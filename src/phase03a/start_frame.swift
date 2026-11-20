import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

enum FrameError: Error {
    case source(URL)
    case bitmap
    case output(URL)
}

let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true)
let arguments = CommandLine.arguments.dropFirst()
let vanityReach = arguments.first == "--vanity-reach"
let holding = arguments.first == "--holding"
let holdingMatte = arguments.first == "--holding-matte"
let episodeCutout = arguments.first == "--episode-cutout"
let roomFile = root.appendingPathComponent(holding
    ? "src/phase02/art/room_clean_plate.png"
    : "assets/environment/APPROVED_lalin_room_master.png")
let poseFile = root.appendingPathComponent(
    "assets/character/approved_initial_3/01_lalin_full_body_primary.png"
)
let width = 1080
let height = 1920
let heroLeft: CGFloat = -263
let heroTop: CGFloat = 515
let heroZoom: CGFloat = 2.83
let colorSpace = CGColorSpace(name: CGColorSpace.sRGB)!
let rgba = CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue

func read(_ url: URL) throws -> CGImage {
    guard let decoder = CGImageSourceCreateWithURL(url as CFURL, nil),
          let result = CGImageSourceCreateImageAtIndex(decoder, 0, nil) else {
        throw FrameError.source(url)
    }
    return result
}

func context(_ width: Int, _ height: Int) throws -> CGContext {
    guard let bitmap = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
                                 bytesPerRow: width * 4, space: colorSpace, bitmapInfo: rgba) else {
        throw FrameError.bitmap
    }
    return bitmap
}

func matte(_ pose: CGImage) throws -> CGImage {
    // The approved master has neutral paper at RGB 253–255. Keep the original
    // painted pixels in the interior and unmix white only at the silhouette.
    let bounds = CGRect(x: 0, y: 0, width: 488, height: vanityReach || episodeCutout ? 660 : 570)
    guard let crop = pose.cropping(to: bounds) else { throw FrameError.bitmap }
    let buffer = try context(crop.width, crop.height)
    buffer.draw(crop, in: bounds)
    guard let pointer = buffer.data?.assumingMemoryBound(to: UInt8.self) else {
        throw FrameError.bitmap
    }
    let count = crop.width * crop.height
    let original = Array(UnsafeBufferPointer(start: pointer, count: count * 4))
    let paper = 254.0
    let paperThreshold = 9
    var signal = [Int](repeating: 0, count: count)
    for index in 0..<count {
        let pixel = index * 4
        signal[index] = Int(paper) - Int(min(original[pixel], original[pixel+1], original[pixel+2]))
    }

    for y in 0..<crop.height {
        for x in 0..<crop.width {
            let index = y * crop.width + x
            let pixel = index * 4
            // In this framing colored decor sits behind the eyes. The white
            // paint inside both outlined eyes belongs to the character.
            if (vanityReach || holding || episodeCutout) && (200...324).contains(x) && (96...134).contains(y) {
                continue
            }
            let value = signal[index]
            if value > paperThreshold {
                var adjacentPaper = false
                var deepest = 46
                for row in max(y-2, 0)...min(y+2, crop.height-1) {
                    for col in max(x-2, 0)...min(x+2, crop.width-1) {
                        let neighbor = signal[row * crop.width + col]
                        adjacentPaper = adjacentPaper || neighbor <= paperThreshold
                        deepest = max(deepest, neighbor)
                    }
                }
                if !adjacentPaper { continue }
                let alpha = min(1.0, Double(value - 5) / Double(deepest - 5))
                for channel in 0..<3 {
                    let unmixed = Double(original[pixel+channel]) - paper*(1.0-alpha)
                    pointer[pixel+channel] = UInt8(max(0, min(255*alpha, unmixed)).rounded())
                }
                pointer[pixel+3] = UInt8((255 * alpha).rounded())
            } else {
                // Retain isolated white-painted highlights away from the paper.
                var isPainted = x > 0 && x+1 < crop.width && y > 0 && y+1 < crop.height
                if isPainted {
                    for dy in -1...1 {
                        for dx in -1...1 where dx != 0 || dy != 0 {
                            isPainted = isPainted && signal[(y+dy)*crop.width+x+dx] > 18
                        }
                    }
                }
                if !isPainted {
                    for channel in 0..<4 { pointer[pixel+channel] = 0 }
                }
            }
        }
    }
    guard let image = buffer.makeImage() else { throw FrameError.bitmap }
    return image
}

let room = try read(roomFile)
let character = try matte(read(poseFile))
let canvas = try context(width, height)
canvas.interpolationQuality = .high

func layer(_ image: CGImage, left: CGFloat, top: CGFloat, zoom: CGFloat) {
    let w = CGFloat(image.width) * zoom
    let h = CGFloat(image.height) * zoom
    canvas.draw(image, in: CGRect(x: left, y: CGFloat(height) - top - h, width: w, height: h))
}

func heldLipstick(over character: CGImage, left: CGFloat, top: CGFloat, zoom: CGFloat) throws {
    let file = root.appendingPathComponent("src/phase02/art/lipstick.png")
    let tube = try read(file)
    let base = CGPoint(x: 313, y: 252)
    let tubeZoom = 0.92 * zoom
    canvas.saveGState()
    canvas.translateBy(x: left + base.x * zoom, y: CGFloat(height) - top - base.y * zoom)
    canvas.rotate(by: -16 * .pi / 180)
    canvas.draw(tube, in: CGRect(x: -14.5 * tubeZoom, y: -2.2 * tubeZoom,
                                width: CGFloat(tube.width) * tubeZoom,
                                height: CGFloat(tube.height) * tubeZoom))
    canvas.restoreGState()

    // Bring the painted fingertips and knuckles forward over the same tube.
    func point(_ x: CGFloat, _ y: CGFloat) -> CGPoint {
        CGPoint(x: left + x * zoom, y: CGFloat(height) - top - y * zoom)
    }
    let fingers = CGMutablePath()
    fingers.move(to: point(290, 194))
    fingers.addQuadCurve(to: point(337, 181), control: point(317, 179))
    fingers.addCurve(to: point(352, 213), control1: point(343, 180), control2: point(348, 194))
    fingers.addQuadCurve(to: point(327, 215), control: point(347, 225))
    fingers.addQuadCurve(to: point(320, 207), control: point(324, 210))
    fingers.addQuadCurve(to: point(314, 216), control: point(315, 207))
    fingers.addQuadCurve(to: point(313, 230), control: point(318, 224))
    fingers.addQuadCurve(to: point(306, 224), control: point(307, 236))
    fingers.addQuadCurve(to: point(299, 233), control: point(303, 232))
    fingers.addQuadCurve(to: point(303, 202), control: point(298, 216))
    fingers.closeSubpath()
    canvas.saveGState()
    canvas.addPath(fingers)
    canvas.clip()
    layer(character, left: left, top: top, zoom: zoom)
    canvas.restoreGState()
}

func expressionMatte() {
    let anchors: [CGPoint] = [
        CGPoint(x: 189, y: 86), CGPoint(x: 207, y: 52),
        CGPoint(x: 243, y: 37), CGPoint(x: 282, y: 39),
        CGPoint(x: 309, y: 51), CGPoint(x: 329, y: 77),
        CGPoint(x: 335, y: 114), CGPoint(x: 332, y: 143),
        CGPoint(x: 315, y: 168), CGPoint(x: 289, y: 176),
        CGPoint(x: 254, y: 173), CGPoint(x: 225, y: 164),
        CGPoint(x: 204, y: 149), CGPoint(x: 191, y: 128)
    ].map { CGPoint(x: heroLeft + $0.x * heroZoom,
                    y: CGFloat(height) - heroTop - $0.y * heroZoom) }
    func midpoint(_ a: CGPoint, _ b: CGPoint) -> CGPoint {
        CGPoint(x: (a.x + b.x) / 2, y: (a.y + b.y) / 2)
    }
    let oval = CGMutablePath()
    oval.move(to: midpoint(anchors[anchors.count - 1], anchors[0]))
    for i in anchors.indices {
        let following = anchors[(i + 1) % anchors.count]
        oval.addQuadCurve(to: midpoint(anchors[i], following), control: anchors[i])
    }
    oval.closeSubpath()
    canvas.setFillColor(gray: 0, alpha: 1)
    canvas.fill(CGRect(x: 0, y: 0, width: width, height: height))
    canvas.setFillColor(gray: 1, alpha: 1)
    canvas.addPath(oval)
    canvas.fillPath()
}

// Optical detail shot at the vanity end of the approved room. One uniform
// camera scale retains furniture placement and the original aspect ratio.
if holdingMatte {
    expressionMatte()
} else {
    let roomZoom = CGFloat(height) / CGFloat(room.height)
    layer(room, left: -1003 * roomZoom, top: 0, zoom: roomZoom)
    if vanityReach {
        // Leave the native lipstick and its surrounding counter unobstructed.
        layer(character, left: -318, top: 480, zoom: 2.27)
    } else {
        layer(character, left: heroLeft, top: heroTop, zoom: heroZoom)
        if holding { try heldLipstick(over: character, left: heroLeft, top: heroTop, zoom: heroZoom) }
    }
}

let defaultPath: String
if vanityReach {
    defaultPath = "outputs/phase03b/lalin_start_frame.png"
} else if holding {
    defaultPath = "outputs/phase03c/start_plan03.png"
} else if holdingMatte {
    defaultPath = "outputs/phase03c/face_matte.png"
} else if episodeCutout {
    defaultPath = "outputs/episode01/lalin_cutout.png"
} else {
    defaultPath = "outputs/phase03a/lalin_start_frame.png"
}
let path = arguments.dropFirst(vanityReach || holding || holdingMatte || episodeCutout ? 1 : 0).first ?? defaultPath
let output = URL(fileURLWithPath: path, relativeTo: root)
try FileManager.default.createDirectory(at: output.deletingLastPathComponent(),
                                       withIntermediateDirectories: true)
guard let result = episodeCutout ? character : canvas.makeImage(),
      let encoded = CGImageDestinationCreateWithURL(output as CFURL, UTType.png.identifier as CFString, 1, nil) else {
    throw FrameError.output(output)
}
CGImageDestinationAddImage(encoded, result, nil)
guard CGImageDestinationFinalize(encoded) else { throw FrameError.output(output) }
