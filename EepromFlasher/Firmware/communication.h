#ifndef COMMUNICATION_H
#define COMMUNICATION_H

/*
 *
 * Communication Protocol Byte Pattern
 *
 * The communication protocol primarily uses a 4-byte structure for
 * single-byte operations. For higher throughput, variable-length
 * block operations are also supported (see OPERATION_*_BLOCK below).
 *
 * General Structure (single byte ops):
 *   Byte 1: Operation Type
 *   Byte 2: Address (High Byte) / Not used
 *   Byte 3: Address (Low Byte) / Not used
 *   Byte 4: Data / Not used
 *
 * Block Operations:
 *   WRITE_BLOCK:
 *     TX -> MCU: [OpType, AddrH, AddrL, Length, Data0..Data(Length-1)]
 *     MCU -> TX: [ACK_WRITE_OK | ACK_WRITE_NO]
 *
 *   READ_BLOCK:
 *     TX -> MCU: [OpType, AddrH, AddrL, Length]
 *     MCU -> TX: [Data0..Data(Length-1), ACK_READ_OK | ACK_READ_NO]
 *
 * The usage of bytes for different operations is as follows:
 *
 * +-----------+------------------+--------------+-------------+----------+
 * | Operation | Byte 1 (OpType)  | Byte 2       | Byte 3      | Byte 4   |
 * +-----------+------------------+--------------+-------------+----------+
 * | WRITE     | Command for Write| Address High | Address Low | Data     |
 * | READ      | Command for Read | Address High | Address Low | Not Used |
 * | RESET     | Command for Reset| Not Used     | Not Used    | Not Used |
 * +-----------+------------------+--------------+-------------+----------+
 */

typedef enum operationType {
    OPERATION_WRITE       = 0x10, // Command for Write
    OPERATION_READ        = 0x20, // Command for Read
    OPERATION_INS_FW      = 0x30, // Command for Instruction Firmware
    OPERATION_INS_DONE    = 0x40, // Command for Instruction Done
    OPERATION_WRITE_BLOCK = 0x50, // Command for Write Block
    OPERATION_READ_BLOCK  = 0x60, // Command for Read Block
    OPERATION_UNKNOWN     = 0xFF  // Unknown operation
} opMode_t;

typedef enum ack {
    ACK_WRITE_OK          = 0x1A, // Acknowledgment for successful write
    ACK_READ_OK           = 0x2A, // Acknowledgment for successful read
    ACK_INS_FW_OK         = 0x3A, // Acknowledgment for successful instruction firmware
    ACK_INS_DONE_OK       = 0x4A, // Acknowledgment for successful instruction done

    ACK_WRITE_NO          = 0x15, // Acknowledgment for unsuccessful write
    ACK_READ_NO           = 0x25, // Acknowledgment for unsuccessful read
    ACK_INS_FW_NO         = 0x35, // Acknowledgment for unsuccessful instruction firmware
    ACK_INS_DONE_NO       = 0x45, // Acknowledgment for unsuccessful instruction done

    ACK_OTHER_NO          = 0xF5  // Acknowledgment for other errors
} ack_t;

typedef enum payloadSize {
    PAYLOAD_SIZE_OP_WRITE     = 3,    // | H Address | L Address | Data |
    PAYLOAD_SIZE_OP_READ      = 2,    // | H Address | L Address |
    PAYLOAD_SIZE_OP_INS_FW    = 1,    // | Dummy Byte |
    PAYLOAD_SIZE_OP_INS_DONE  = 1,    // | Dummy Byte |
    // For block ops, we first read 3 bytes (H,L,Len), then variable payload.
    PAYLOAD_SIZE_OP_BLOCK_HDR = 3,    // | H Address | L Address | Length |
    PAYLOAD_SIZE_MAX          = 3     // Maximum fixed-size portion read at once
} payloadSize_t;


typedef enum returnCode {
    RET_OK                    = 0,    // Operation successful
    RET_ERROR                 = 1,   // General error
    RET_INVALID_OPERATION     = 2,   // Invalid operation type
    RET_PAYLOAD_TOO_SHORT     = 3,   // Payload too short for operation
    RET_PAYLOAD_TOO_LONG      = 4,   // Payload too long for operation
    RET_UNSUPPORTED_OPERATION = 5    // Operation not supported
} returnCode_t;


typedef enum payloadIndex {
    IDX_H_ADDRESS   = 0,    // High byte of address
    IDX_L_ADDRESS   = 1,    // Low byte of address
    IDX_LEN         = 2,    // Length byte for block operations
    IDX_DATA        = 2     // Data byte for write operation
} payloadIndex_t;


#define DEFAULT_CHUNK_SIZE  64

#endif // COMMUNICATION_H
