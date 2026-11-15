import Foundation

struct Brief: Codable, Equatable, Sendable {
    var freeText = ""
    var schoolContext = ""
    var studentProfile = ""
    var startingKnowledge = ""
    var objectives = ""
    var topics = ""
    var organisation = ""
    var preferences = ""
}

struct Program: Codable, Identifiable, Equatable, Sendable {
    var id: String
    var title: String
    var classLabel: String
    var description: String
    var brief: Brief
    var createdAt: String
    var updatedAt: String
    var revision: Int
}

struct ProgramDraft: Equatable {
    var title = ""
    var classLabel = ""
    var description = ""
    var brief = Brief()

    init() {}
    init(_ program: Program) {
        title = program.title
        classLabel = program.classLabel
        description = program.description
        brief = program.brief
    }
}

struct LocalSettings: Codable, Sendable {
    var dataDirectory: String
    var exportDirectory: String
}

struct AccountStatus: Codable, Sendable {
    var installed: Bool
    var connected: Bool
    var authentication: String?
    var email: String?
    var plan: String?
    var usedPercent: Double?
    var resetsAt: Double?
    var version: String?
    var message: String
}

enum JSONValue: Codable, Sendable {
    case object([String: JSONValue]), array([JSONValue]), string(String), number(Double), bool(Bool), null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() { self = .null }
        else if let value = try? container.decode(Bool.self) { self = .bool(value) }
        else if let value = try? container.decode(String.self) { self = .string(value) }
        else if let value = try? container.decode(Double.self) { self = .number(value) }
        else if let value = try? container.decode([String: JSONValue].self) { self = .object(value) }
        else { self = .array(try container.decode([JSONValue].self)) }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .object(let value): try container.encode(value)
        case .array(let value): try container.encode(value)
        case .string(let value): try container.encode(value)
        case .number(let value): try container.encode(value)
        case .bool(let value): try container.encode(value)
        case .null: try container.encodeNil()
        }
    }

    subscript(_ key: String) -> JSONValue? {
        if case .object(let value) = self { return value[key] }
        return nil
    }
    var string: String? { if case .string(let value) = self { return value }; return nil }
    var integer: Int? { if case .number(let value) = self { return Int(value) }; return nil }
}

struct EngineError: LocalizedError {
    let message: String
    var errorDescription: String? { message }
}

func decode<T: Decodable>(_ type: T.Type, from value: JSONValue) throws -> T {
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    return try decoder.decode(type, from: JSONEncoder().encode(value))
}

func encode<T: Encodable>(_ value: T) throws -> JSONValue {
    let encoder = JSONEncoder()
    encoder.keyEncodingStrategy = .convertToSnakeCase
    return try JSONDecoder().decode(JSONValue.self, from: encoder.encode(value))
}
