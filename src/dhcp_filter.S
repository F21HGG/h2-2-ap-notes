.syntax unified
.arm
.global _start
.text
_start:
    ldr r0, [sp]
    cmp r0, #3
    bne fail
    ldr r0, [sp, #8]
    ldrb r1, [r0]
    cmp r1, #119
    beq wifi
    cmp r1, #101
    beq ethernet
    b fail
wifi:
    ldrb r1, [r0, #1]
    cmp r1, #108
    bne fail
    ldrb r1, [r0, #2]
    cmp r1, #97
    bne fail
    ldrb r1, [r0, #3]
    cmp r1, #110
    bne fail
    ldrb r1, [r0, #4]
    cmp r1, #48
    beq wifi_tail
    cmp r1, #52
    bne fail
wifi_tail:
    ldrb r1, [r0, #5]
    cmp r1, #0
    bne fail
    b args
ethernet:
    ldrb r1, [r0, #1]
    cmp r1, #116
    bne fail
    ldrb r1, [r0, #2]
    cmp r1, #104
    bne fail
    ldrb r1, [r0, #3]
    cmp r1, #50
    bne fail
    ldrb r1, [r0, #4]
    cmp r1, #0
    bne fail
args:
    ldr r2, [sp, #12]
    ldrb r3, [r2]
    cmp r3, #48
    beq action_ok
    cmp r3, #49
    bne fail
    mov r3, #1
    b action_tail
action_ok:
    mov r3, #0
action_tail:
    ldrb r2, [r2, #1]
    cmp r2, #0
    bne fail
    mov r8, r0
    mov r9, r3
    cmp r9, #1
    bne apply
    sub sp, sp, #8192
    adr r0, procpath
    mov r1, #0
    mov r2, #0
    mov r7, #5
    svc #0
    cmp r0, #0
    blt fail
    mov r6, r0
    mov r1, sp
    mov r2, #8192
    mov r7, #3
    svc #0
    cmp r0, #0
    ble fail
    add r11, sp, r0
    mov r0, r6
    mov r7, #6
    svc #0
    mov r4, sp
    b find_line
.align 2
procpath: .asciz "/proc/net/brport"
.align 2
name_prefix: .asciz "Name:["
.align 2
open_pattern: .asciz "Ifwd.Type:[1], Ifwd.Protocol:[10]"
.align 2
find_line:
    cmp r4, r11
    bhs fail
    ldrb r0, [r4], #1
    cmp r0, #78
    bne find_line
    sub r5, r4, #1
    adr r6, name_prefix
prefix_loop:
    ldrb r0, [r6], #1
    cmp r0, #0
    beq prefix_found
    cmp r5, r11
    bhs fail
    ldrb r1, [r5], #1
    cmp r0, r1
    bne find_line
    b prefix_loop
prefix_found:
    mov r6, r8
name_loop:
    ldrb r0, [r6], #1
    cmp r0, #0
    beq name_end
    cmp r5, r11
    bhs fail
    ldrb r1, [r5], #1
    cmp r0, r1
    bne find_line
    b name_loop
name_end:
    cmp r5, r11
    bhs fail
    ldrb r0, [r5], #1
    cmp r0, #93
    bne find_line
scan_field:
    cmp r5, r11
    bhs fail
    ldrb r0, [r5], #1
    cmp r0, #10
    beq fail
    cmp r0, #73
    bne scan_field
    sub r6, r5, #1
    adr r10, open_pattern
pattern_loop:
    ldrb r0, [r10], #1
    cmp r0, #0
    beq pattern_found
    cmp r6, r11
    bhs fail
    ldrb r1, [r6], #1
    cmp r0, r1
    bne scan_field
    b pattern_loop
pattern_found:
    add sp, sp, #8192
apply:
    mov r0, r8
    mov r3, r9
    sub sp, sp, #96
    mov r5, sp
    mov r7, #0
    mov r2, #24
clear:
    str r7, [r5], #4
    subs r2, r2, #1
    bne clear
    add r5, sp, #0
    str r7, [r5]
    add r6, r5, #4
copy:
    ldrb r1, [r0], #1
    strb r1, [r6], #1
    cmp r1, #0
    bne copy
    mov r1, #1
    str r1, [r5, #20]
    mov r1, #4
    str r1, [r5, #24]
    mov r1, #1
    str r1, [r5, #28]
    add r6, sp, #32
    mov r1, #94
    str r1, [r6]
    str r5, [r6, #4]
    str r3, [r6, #8]
    add r4, sp, #48
    mov r1, #98
    strb r1, [r4]
    mov r1, #114
    strb r1, [r4, #1]
    mov r1, #48
    strb r1, [r4, #2]
    str r6, [r4, #16]
    mov r0, #2
    mov r1, #1
    mov r2, #0
    movw r7, #281
    svc #0
    cmp r0, #0
    blt fail
    mov r5, r0
    movw r1, #0x89f0
    mov r2, r4
    mov r7, #54
    svc #0
    cmp r0, #0
    bne fail
    mov r0, r5
    mov r7, #6
    svc #0
    mov r0, #0
    mov r7, #1
    svc #0
fail:
    mov r0, #1
    mov r7, #1
    svc #0
