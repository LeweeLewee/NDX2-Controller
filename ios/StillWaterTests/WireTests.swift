import XCTest
@testable import StillWater

final class WireTests: XCTestCase {
    func vectors() throws -> [String: JSONValue] {
        let url = try XCTUnwrap(Bundle.main.url(forResource:"BridgeFixtures",withExtension:"json"))
        return try JSONDecoder().decode([String:JSONValue].self,from:Data(contentsOf:url))
    }
    func testAllPythonContractVectorsDecode() throws {
        for (name,v) in try vectors() {
            let request = try JSONDecoder().decode(BridgeRequest.self,from:JSONEncoder().encode(v["request"]))
            let reply = try BridgeReply.decode(JSONEncoder().encode(v["reply"]),for:request)
            XCTAssertEqual(reply.outcome,"observed",name); XCTAssertTrue(reply.fixture)
        }
    }
    func testEnvelopeBoundsIdentityAndTypes() throws {
        let v = try XCTUnwrap(vectors()["snapshot"])
        let request = try JSONDecoder().decode(BridgeRequest.self,from:JSONEncoder().encode(v["request"]))
        guard case .object(let base) = v["reply"] else { return XCTFail() }
        for (key,value) in [("version",JSONValue.bool(true)),("version",.int(2)),("request_id",.string("wrong")),("boot_id",.string("wrong")),("fixture",.int(1)),("outcome",.string("submitted"))] {
            var bad = base; bad[key] = value
            XCTAssertThrowsError(try BridgeReply.decode(JSONEncoder().encode(JSONValue.object(bad)),for:request))
        }
        XCTAssertThrowsError(try BridgeReply.decode(Data(repeating:32,count:32769),for:request))
    }
    func testNormalizedPlayerStatesAndMembershipFromBridge() throws {
        let values = try vectors()
        for state in ["playing","paused","stopped"] {
            let vector = try XCTUnwrap(values["snapshot-"+state])
            XCTAssertEqual(Player(vector["reply"]["data"]["player"]).state,state)
        }
        let page = try XCTUnwrap(values["search-albums"])
        XCTAssertEqual(page["reply"]["data"]["items"].values.prefix(3).map { MusicItem($0).saved },["saved","unsaved","unknown"])
    }
    func testFull320AssemblyAndChangedImageRefusal() throws {
        let values = try vectors()
        let first = try XCTUnwrap(values["artwork-0"])
        let ref = try XCTUnwrap(first["request"]["args"]["reference"].text)
        var art = ArtworkAssembly(reference:ref,side:320)
        for offset in stride(from:0,to:102400,by:6400) {
            let v = try XCTUnwrap(values["artwork-\(offset)"])
            let req = try JSONDecoder().decode(BridgeRequest.self,from:JSONEncoder().encode(v["request"]))
            let reply = try BridgeReply.decode(JSONEncoder().encode(v["reply"]),for:req)
            try art.append(reply,started:100,now:101)
        }
        XCTAssertTrue(art.complete); XCTAssertEqual(art.bytes.count,204800)
        let req = try JSONDecoder().decode(BridgeRequest.self,from:JSONEncoder().encode(first["request"]))
        let reply = try BridgeReply.decode(JSONEncoder().encode(first["reply"]),for:req)
        XCTAssertThrowsError(try art.append(reply,started:100,now:101))
        var fresh = ArtworkAssembly(reference:ref,side:320)
        XCTAssertThrowsError(try fresh.append(reply,started:100,now:160))
        try fresh.append(reply,started:100,now:101)
        let second = try XCTUnwrap(values["artwork-6400"])
        guard case .object(var root) = second["reply"], case .object(var data) = root["data"] else { return XCTFail() }
        data["image_id"] = .string(String(repeating:"f",count:64)); root["data"] = .object(data)
        let request = try JSONDecoder().decode(BridgeRequest.self,from:JSONEncoder().encode(second["request"]))
        let changed = try BridgeReply.decode(JSONEncoder().encode(JSONValue.object(root)),for:request)
        XCTAssertThrowsError(try fresh.append(changed,started:100,now:102))
    }
    func testOriginRefusesCredentialsAndInsecureRoutes() throws {
        for text in ["http://localhost", "https://user:pass@host", "https://host/path", "https://host?key=value", "https://host#trust"] {
            XCTAssertThrowsError(try Enrollment.origin(text))
        }
        XCTAssertEqual(try Enrollment.origin("https://localhost:8991").host,"localhost")
    }    func testBiographySpecificBoundDoesNotWidenOtherText() throws {
        XCTAssertNoThrow(try JSONValue.object(["biography":.string(String(repeating:"🎵",count:2000))]).bounded())
        XCTAssertThrowsError(try JSONValue.object(["biography":.string(String(repeating:"a",count:2001))]).bounded())
        XCTAssertThrowsError(try JSONValue.object(["title":.string(String(repeating:"a",count:257))]).bounded())
    }

}
