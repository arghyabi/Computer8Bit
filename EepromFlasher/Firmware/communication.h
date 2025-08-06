#ifndef COMMUNICATION_H
#define COMMUNICATION_H

/*
 *
 * Communication Protocol Byte Pattern
 *
 * The communication protocol uses a 4-byte structure. The first byte
 * specifies the operation type, and the subsequent bytes' meanings
 * depend on that type.
 *
 * General Structure:
 *   Byte 1: Operation Type
 *   Byte 2: Address (High Byte) / Not used
 *   Byte 3: Address (Low Byte) / Not used
 *   Byte 4: Data / Not used
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
    PAYLOAD_SIZE_OP_INS_FW    = 0,    // |
    PAYLOAD_SIZE_OP_INS_DONE  = 0,    // |
    PAYLOAD_SIZE_MAX          = 3     // Maximum frame size for any operation
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
    IDX_DATA        = 2     // Data byte for write operation
} payloadIndex_t;


#endif // COMMUNICATION_H
