PX       = $30
PY       = $31
CHR      = $32
PTR_L    = $33
PTR_H    = $34
NX       = $35
NY       = $36
DIR      = $37
NEXTDIR  = $38
HEAD     = $39
TAIL     = $3A
SCORE    = $3B
SEED     = $3C
ATE      = $3D
TIMER    = $3E
TMP2     = $3F
SAVESP   = $40
SX       = $3000
SY       = $3100
ROWL     = $3200
ROWH     = $3300
KEYSTAT  = $0201
KEYDATA  = $0200
SPEED    = 15
C_WALL   = $23
C_BODY   = $6F
C_HEAD   = $40
C_APPLE  = $2A
C_SPACE  = $20

    .ORG $2100

START:
    TSX
    STX SAVESP
    JSR INIT
WAITKEY:
    INC SEED
    LDA KEYSTAT
    BEQ WAITKEY
    LDA KEYDATA

MAIN:
    LDA NEXTDIR
    STA DIR
    LDX HEAD
    LDA SX,X
    STA NX
    LDA SY,X
    STA NY
    LDA DIR
    CMP #$00
    BEQ D_UP
    CMP #$01
    BEQ D_DOWN
    CMP #$02
    BEQ D_LEFT
    INC NX
    JMP D_OK
D_UP:
    DEC NY
    JMP D_OK
D_DOWN:
    INC NY
    JMP D_OK
D_LEFT:
    DEC NX
D_OK:
    LDX NY
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDY NX
    LDA (PTR_L),Y
    CMP #C_SPACE
    BEQ M_MOVE
    CMP #C_APPLE
    BEQ M_EAT
    JMP GAME_OVER
M_EAT:
    LDA #$01
    STA ATE
    JMP M_GO
M_MOVE:
    LDA #$00
    STA ATE
M_GO:
    LDX HEAD
    LDA SX,X
    STA PX
    LDA SY,X
    STA PY
    LDA #C_BODY
    STA CHR
    JSR DRAW_AT
    INC HEAD
    LDX HEAD
    LDA NX
    STA SX,X
    STA PX
    LDA NY
    STA SY,X
    STA PY
    LDA #C_HEAD
    STA CHR
    JSR DRAW_AT
    LDA ATE
    BNE M_ATE
    LDX TAIL
    LDA SX,X
    STA PX
    LDA SY,X
    STA PY
    LDA #C_SPACE
    STA CHR
    JSR DRAW_AT
    INC TAIL
    JMP M_NEXT
M_ATE:
    INC SCORE
    JSR PRINT_SCORE
    JSR NEW_APPLE
M_NEXT:
    LDA #SPEED
    STA TIMER
WAIT:
    INC SEED
    JSR READKEYS
    LDX #$FF
W2:
    DEX
    BNE W2
    DEC TIMER
    BNE WAIT
    JMP MAIN

READKEYS:
    LDA KEYSTAT
    BEQ RK_DONE
    LDA KEYDATA
    CMP #$51
    BEQ RK_QUIT
    LDX #$00
    CMP #$57
    BEQ RK_SET
    LDX #$01
    CMP #$53
    BEQ RK_SET
    LDX #$02
    CMP #$41
    BEQ RK_SET
    LDX #$03
    CMP #$44
    BEQ RK_SET
    JMP READKEYS
RK_SET:
    TXA
    EOR #$01
    CMP DIR
    BEQ READKEYS
    STX NEXTDIR
    JMP READKEYS
RK_QUIT:
    JMP QUIT
RK_DONE:
    RTS

DRAW_AT:
    LDX PY
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDY PX
    LDA CHR
    STA (PTR_L),Y
    RTS

RAND:
    LDA SEED
    BNE RN_OK
    LDA #$5A
RN_OK:
    ASL A
    BCC RN_DONE
    EOR #$1D
RN_DONE:
    STA SEED
    RTS

NEW_APPLE:
    JSR RAND
    AND #$3F
NA_X:
    CMP #$26
    BCC NA_XD
    SBC #$26
    BCS NA_X
NA_XD:
    CLC
    ADC #$01
    STA PX
    JSR RAND
    AND #$1F
NA_Y:
    CMP #$17
    BCC NA_YD
    SBC #$17
    BCS NA_Y
NA_YD:
    CLC
    ADC #$01
    STA PY
    TAX
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDY PX
    LDA (PTR_L),Y
    CMP #C_SPACE
    BNE NEW_APPLE
    LDA #C_APPLE
    STA (PTR_L),Y
    RTS

PRINT_SCORE:
    LDA SCORE
    LDX #$00
PS_H:
    CMP #$64
    BCC PS_HD
    SBC #$64
    INX
    BNE PS_H
PS_HD:
    STA TMP2
    TXA
    CLC
    ADC #$30
    STA $0408
    LDA TMP2
    LDX #$00
PS_T:
    CMP #$0A
    BCC PS_TD
    SBC #$0A
    INX
    BNE PS_T
PS_TD:
    STA TMP2
    TXA
    CLC
    ADC #$30
    STA $0409
    LDA TMP2
    CLC
    ADC #$30
    STA $040A
    RTS

INIT:
    LDA #$00
    STA PTR_L
    LDA #$04
    STA PTR_H
    LDX #$00
RT_LOOP:
    LDA PTR_L
    STA ROWL,X
    LDA PTR_H
    STA ROWH,X
    CLC
    LDA PTR_L
    ADC #$28
    STA PTR_L
    BCC RT_NC
    INC PTR_H
RT_NC:
    INX
    CPX #$19
    BNE RT_LOOP
    LDA #C_SPACE
    LDX #$00
CL_LOOP:
    STA $0400,X
    STA $0500,X
    STA $0600,X
    STA $0700,X
    INX
    BNE CL_LOOP
    LDA #C_WALL
    LDX #$00
BD_LOOP:
    STA $0400,X
    STA $07C0,X
    INX
    CPX #$28
    BNE BD_LOOP
    LDX #$01
SD_LOOP:
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    LDA #C_WALL
    LDY #$00
    STA (PTR_L),Y
    LDY #$27
    STA (PTR_L),Y
    INX
    CPX #$18
    BNE SD_LOOP
    LDA #$14
    STA SX
    STA PX
    LDA #$0C
    STA SY
    STA PY
    LDA #$00
    STA HEAD
    STA TAIL
    STA SCORE
    LDA #$03
    STA DIR
    STA NEXTDIR
    LDA #$A5
    STA SEED
    LDA #C_HEAD
    STA CHR
    JSR DRAW_AT
    JSR NEW_APPLE
    LDA #$53
    STA $0402
    LDA #$43
    STA $0403
    LDA #$4F
    STA $0404
    LDA #$52
    STA $0405
    LDA #$45
    STA $0406
    LDA #$3A
    STA $0407
    JSR PRINT_SCORE
    RTS

GAME_OVER:
    LDA #$47
    STA $05EF
    LDA #$41
    STA $05F0
    LDA #$4D
    STA $05F1
    LDA #$45
    STA $05F2
    LDA #$4F
    STA $05F4
    LDA #$56
    STA $05F5
    LDA #$45
    STA $05F6
    LDA #$52
    STA $05F7
    LDY #$40
GO_D1:
    LDX #$FF
GO_D2:
    DEX
    BNE GO_D2
    DEY
    BNE GO_D1
GO_FL: ;throw away anything typed during the pause
    LDA KEYSTAT
    BEQ GO_WAIT
    LDA KEYDATA
    JMP GO_FL
GO_WAIT:
    LDA KEYSTAT
    BEQ GO_WAIT
    LDA KEYDATA

QUIT: ;back to the shell
    LDX SAVESP
    TXS
    RTS
