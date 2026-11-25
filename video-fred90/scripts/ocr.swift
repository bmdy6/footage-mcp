import Foundation
import Vision
import AppKit
let dir = URL(fileURLWithPath: CommandLine.arguments[1])
var output: [[String: Any]] = []
for url in try FileManager.default.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil).sorted(by: {$0.lastPathComponent < $1.lastPathComponent}) where ["jpg", "png"].contains(url.pathExtension) {
 let request = VNRecognizeTextRequest()
 request.recognitionLevel = .accurate
 request.recognitionLanguages = ["zh-Hans", "en-US"]
 request.usesLanguageCorrection = false
 do {
  try VNImageRequestHandler(url: url).perform([request])
  let rows = (request.results ?? []).compactMap { o -> [String:Any]? in
   guard let c = o.topCandidates(1).first else {return nil}
   return ["text":c.string,"confidence":c.confidence,"box":[o.boundingBox.minX,1-o.boundingBox.maxY,o.boundingBox.width,o.boundingBox.height]]
  }
  output.append(["frame": url.lastPathComponent, "rows":rows])
 } catch { fputs("OCR failed \(url): \(error)\n",stderr) }
}
let data = try JSONSerialization.data(withJSONObject: output, options: [.prettyPrinted,.sortedKeys,.withoutEscapingSlashes])
try data.write(to:URL(fileURLWithPath:CommandLine.arguments[2]))
print("OCR \(output.count) frames")
