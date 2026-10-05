PX = $30
PY = $31
HP = $50
GOLD = $51
ROOM = $34
SAVESP = $35
PTR_L = $36
PTR_H = $37
SEED = $38
TGT_X = $39
TGT_Y = $3A
ROOM_W = $3B
ROOM_H = $3C
MON_X = $3D
MON_Y = $3E

M1_TYPE = $40
M1_X = $41
M1_Y = $42
M1_HP = $43
M2_TYPE = $44
M2_X = $45
M2_Y = $46
M2_HP = $47
GOLD_X = $48
GOLD_Y = $49
GOLD_X2 = $4A
GOLD_Y2 = $4B
G_CNT = $4C
M_CNT = $4D

KEYBOARD = $0200
ROWL = $3200
ROWH = $3300

    .ORG $2100

START:
    TSX
    STX SAVESP
    JSR INIT_ROWS
    LDA #$09
    STA HP
    LDA #$01
    STA ROOM
    LDA #$00
    STA GOLD
    LDA #$35
    STA SEED

LOAD:
    JSR GEN_ROOM
    JSR DRAW_MAP
    LDA #$02
    STA PX
    STA PY
    JSR SPAWN_GOLD
    JSR SPAWN_MONS

LOOP:
    JSR DRAW_MAP
    JSR DRAW_FEAT
    JSR DRAW_ENT
    JSR DRAW_STATS

INPUT:
    INC SEED
    LDA KEYBOARD
    BEQ INPUT
    LDY #$00
    STY KEYBOARD
    CMP #$51
    BEQ QUIT
    CMP #$71
    BEQ QUIT
    CMP #$57
    BEQ MV_W
    CMP #$77
    BEQ MV_W
    CMP #$53
    BEQ MV_S
    CMP #$73
    BEQ MV_S
    CMP #$41
    BEQ MV_A
    CMP #$61
    BEQ MV_A
    CMP #$44
    BEQ MV_D
    CMP #$64
    BEQ MV_D
    JMP INPUT

MV_W:
    LDA PX
    STA TGT_X
    LDA PY
    SEC
    SBC #1
    STA TGT_Y
    JMP TRY

MV_S:
    LDA PX
    STA TGT_X
    LDA PY
    CLC
    ADC #1
    STA TGT_Y
    JMP TRY

MV_A:
    LDA PX
    SEC
    SBC #1
    STA TGT_X
    LDA PY
    STA TGT_Y
    JMP TRY

MV_D:
    LDA PX
    CLC
    ADC #1
    STA TGT_X
    LDA PY
    STA TGT_Y
    JMP TRY

TRY:
    LDA TGT_Y
    CMP #$01
    BCC BLOCK
    CMP ROOM_H
    BCS BLOCK
    LDA TGT_X
    CMP #$01
    BCC BLOCK
    CMP ROOM_W
    BCS BLOCK
    LDY TGT_X
    LDX TGT_Y
    JSR SET_PTR
    LDA (PTR_L),Y
    CMP #$23
    BEQ BLOCK
    CMP #$24
    BEQ GOLD_C
    CMP #$45
    BEQ EXIT_C
    LDA M1_TYPE
    BEQ CHK_M2
    LDA TGT_X
    CMP M1_X
    BNE CHK_M2
    LDA TGT_Y
    CMP M1_Y
    BNE CHK_M2
    JSR ATK_M1
    LDA M1_TYPE
    BEQ NO_RET
    JSR RAND
    AND #$01
    BNE NO_RET
    DEC HP
    JMP TURN
CHK_M2:
    LDA M2_TYPE
    BEQ MOVE_OK
    LDA TGT_X
    CMP M2_X
    BNE MOVE_OK
    LDA TGT_Y
    CMP M2_Y
    BNE MOVE_OK
    JSR ATK_M2
    LDA M2_TYPE
    BEQ NO_RET
    JSR RAND
    AND #$01
    BNE NO_RET
    DEC HP
    JMP TURN
NO_RET:
    JMP TURN

GOLD_C:
    LDA #$20
    STA (PTR_L),Y
    LDA #$00
    STA GOLD_X
    STA GOLD_Y
    LDA #$02
    JSR ADD_G
    DEC G_CNT
    LDA TGT_X
    STA PX
    LDA TGT_Y
    STA PY
    JMP TURN
MOVE_OK:
    LDA TGT_X
    STA PX
    LDA TGT_Y
    STA PY
    JMP TURN

BLOCK:
    JMP TURN

EXIT_C:
    LDA #$00
    STA M1_TYPE
    STA M2_TYPE
    STA GOLD_X
    STA GOLD_Y
    STA GOLD_X2
    STA GOLD_Y2
    INC ROOM
    LDA ROOM
    CMP #$0B
    BNE LOAD
    JMP QUIT

TURN:
    JSR PROC_MONS
    LDA HP
    BNE LOOP
    JMP QUIT

ATK_M1:
    JSR RAND
    AND #$03
    BEQ M1_MISS
    DEC M1_HP
    BNE M1_MISS
    LDA M1_TYPE
    JSR REWARD
    LDA #$00
    STA M1_TYPE
M1_MISS:
    RTS

ATK_M2:
    JSR RAND
    AND #$03
    BEQ M2_MISS
    DEC M2_HP
    BNE M2_MISS
    LDA M2_TYPE
    JSR REWARD
    LDA #$00
    STA M2_TYPE
M2_MISS:
    RTS

ADD_G:
    CLC
    ADC GOLD
    CMP #$63
    BCC AG_S
    LDA #$63
AG_S:
    STA GOLD
    RTS

REWARD:
    CMP #$5A
    BEQ R_1
    CMP #$53
    BEQ R_3
    LDA #$05
    JMP ADD_G
R_1:
    LDA #$01
    JMP ADD_G
R_3:
    LDA #$03
    JMP ADD_G

PROC_MONS:
    LDA M1_TYPE
    BEQ PM2
    LDX M1_X
    LDY M1_Y
    JSR MON_ATK
    LDX M1_X
    LDY M1_Y
    JSR STEP_M
    STX M1_X
    STY M1_Y

PM2:
    LDA M2_TYPE
    BEQ PM_D
    LDX M2_X
    LDY M2_Y
    JSR MON_ATK
    LDX M2_X
    LDY M2_Y
    JSR STEP_M
    STX M2_X
    STY M2_Y

PM_D:
    RTS

STEP_M:
    STX PTR_L
    STY PTR_H
    STX MON_X
    STY MON_Y
    LDA SEED
    AND #$01
    BEQ SM_X
SM_Y:
    LDA PY
    CMP MON_Y
    BEQ SM_X
    BCC SM_DY
    INC MON_Y
    JMP SM_CHK
SM_DY:
    DEC MON_Y
    JMP SM_CHK
SM_X:
    LDA PX
    CMP MON_X
    BEQ SM_Y
    BCC SM_DX
    INC MON_X
    JMP SM_CHK
SM_DX:
    DEC MON_X
SM_CHK:
    LDA MON_X
    CMP #$01
    BCC SM_FAIL
    CMP ROOM_W
    BCS SM_FAIL
    LDA MON_Y
    CMP #$01
    BCC SM_FAIL
    CMP ROOM_H
    BCS SM_FAIL
    LDX MON_Y
    JSR SET_PTR
    LDY MON_X
    LDA (PTR_L),Y
    CMP #$23
    BEQ SM_FAIL
    LDA MON_X
    CMP PX
    BNE SM_OK
    LDA MON_Y
    CMP PY
    BEQ SM_FAIL
SM_OK:
    LDX MON_X
    LDY MON_Y
    RTS

SM_FAIL:
    LDX PTR_L
    LDY PTR_H
    RTS

MON_ATK:
    STX TGT_X
    STY TGT_Y
    LDA PX
    SEC
    SBC TGT_X
    BPL MA_X_POS
    STA PTR_L
    LDA #$00
    SEC
    SBC PTR_L
MA_X_POS:
    STA PTR_L
    LDA PY
    SEC
    SBC TGT_Y
    BPL MA_Y_POS
    STA PTR_H
    LDA #$00
    SEC
    SBC PTR_H
MA_Y_POS:
    CLC
    ADC PTR_L
    CMP #$02
    BCS MA_DONE
    LDA HP
    BEQ MA_DONE
    DEC HP
MA_DONE:
    RTS

GEN_ROOM:
    JSR RAND
    AND #$0F
    CLC
    ADC #$0A
    STA ROOM_W
    JSR RAND
    AND #$07
    CLC
    ADC #$06
    STA ROOM_H
    RTS

SPAWN_GOLD:
    JSR RAND
    AND #$03
    BEQ SG_NONE
    CMP #$03
    BEQ SG_NONE
    STA G_CNT
    JSR RAND
    AND #$0F
    CLC
    ADC #$02
    CMP ROOM_W
    BCC SG_X1
    LDA #$03
SG_X1:
    STA GOLD_X
    JSR RAND
    AND #$07
    CLC
    ADC #$02
    CMP ROOM_H
    BCC SG_Y1
    LDA #$03
SG_Y1:
    STA GOLD_Y
    LDA G_CNT
    CMP #$02
    BCC SG_DONE
    JSR RAND
    AND #$0F
    CLC
    ADC #$02
    CMP ROOM_W
    BCC SG_X2
    LDA #$03
SG_X2:
    STA GOLD_X2
    JSR RAND
    AND #$07
    CLC
    ADC #$02
    CMP ROOM_H
    BCC SG_Y2
    LDA #$03
SG_Y2:
    STA GOLD_Y2
SG_DONE:
    RTS
SG_NONE:
    LDA #$00
    STA G_CNT
    STA GOLD_X
    RTS

SPAWN_MONS:
    JSR RAND
    AND #$03
    BEQ SM_NONE
    CMP #$03
    BEQ SM_NONE
    STA M_CNT
    JSR SPAWN_M1
    LDA M_CNT
    CMP #$02
    BCC SM_DONE
    JSR SPAWN_M2
SM_DONE:
    RTS
SM_NONE:
    LDA #$00
    STA M_CNT
    STA M1_TYPE
    STA M2_TYPE
    RTS

SPAWN_M1:
SM1_RETRY:
    JSR RAND
    AND #$03
    TAX
    LDA #$5A
    LDY #$02
    CPX #$01
    BNE SM1_SLIME
    LDA #$53
SM1_SLIME:
    CPX #$02
    BNE SM1_TYPE
    LDA #$47
    LDY #$04
SM1_TYPE:
    STA M1_TYPE
    STY M1_HP
    JSR RAND
    AND #$0F
    CLC
    ADC #$03
    CMP ROOM_W
    BCC SM1_X
    LDA #$04
SM1_X:
    STA M1_X
    JSR RAND
    AND #$07
    CLC
    ADC #$02
    CMP ROOM_H
    BCC SM1_Y
    LDA #$04
SM1_Y:
    STA M1_Y
    LDA M1_X
    CMP #$02
    BNE SM1_OK
    LDA M1_Y
    CMP #$02
    BEQ SM1_RETRY
SM1_OK:
    RTS

SPAWN_M2:
SM2_RETRY:
    JSR RAND
    AND #$03
    TAX
    LDA #$5A
    LDY #$02
    CPX #$01
    BNE SM2_S
    LDA #$53
SM2_S:
    CPX #$02
    BNE SM2_G
    LDA #$47
    LDY #$04
SM2_G:
    STA M2_TYPE
    STY M2_HP
    JSR RAND
    AND #$0F
    CLC
    ADC #$04
    CMP ROOM_W
    BCC SM2_X
    LDA #$05
SM2_X:
    STA M2_X
    JSR RAND
    AND #$07
    CLC
    ADC #$03
    CMP ROOM_H
    BCC SM2_Y
    LDA #$05
SM2_Y:
    STA M2_Y
    LDA M2_X
    CMP M1_X
    BNE SM2_OK
    LDA M2_Y
    CMP M1_Y
    BEQ SM2_RETRY
SM2_OK:
    RTS

RAND:
    LDA SEED
    BNE R_EXEC
    LDA #$A5
    STA SEED
R_EXEC:
    LSR A
    BCS R_XOR
    STA SEED
    RTS
R_XOR:
    EOR #$B4
    STA SEED
    RTS

DRAW_MAP:
    LDX #$00
    LDA #$20
DM_C:
    STA $0400,X
    STA $0500,X
    STA $0600,X
    STA $0700,X
    INX
    BNE DM_C
    LDX #$01
DM_TB:
    LDY #$01
    JSR SET_PTR_Y
    TXA
    TAY
    LDA #$23
    STA (PTR_L),Y
    LDY ROOM_H
    JSR SET_PTR_Y
    TXA
    TAY
    LDA #$23
    STA (PTR_L),Y
    INX
    CPX ROOM_W
    BCC DM_TB
    LDX #$01
DM_LR:
    JSR SET_PTR
    LDA #$23
    LDY #$01
    STA (PTR_L),Y
    LDY ROOM_W
    STA (PTR_L),Y
    INX
    CPX ROOM_H
    BCC DM_LR
    RTS

DRAW_FEAT:
    LDX ROOM_H
    DEX
    JSR SET_PTR
    LDA #$45
    LDY ROOM_W
    DEY
    STA (PTR_L),Y
    LDA GOLD_X
    BEQ DF_D
    LDX GOLD_Y
    JSR SET_PTR
    LDA #$24
    LDY GOLD_X
    STA (PTR_L),Y
    LDA G_CNT
    CMP #$02
    BCC DF_D
    LDA GOLD_X2
    BEQ DF_D
    LDX GOLD_Y2
    JSR SET_PTR
    LDA #$24
    LDY GOLD_X2
    STA (PTR_L),Y
DF_D:
    RTS

DRAW_ENT:
    LDX PY
    JSR SET_PTR
    LDY PX
    LDA #$40
    STA (PTR_L),Y
    LDA M1_TYPE
    BEQ DE_M2
    LDX M1_Y
    JSR SET_PTR
    LDY M1_X
    LDA M1_TYPE
    STA (PTR_L),Y
DE_M2:
    LDA M2_TYPE
    BEQ DE_D
    LDX M2_Y
    JSR SET_PTR
    LDY M2_X
    LDA M2_TYPE
    STA (PTR_L),Y
DE_D:
    RTS

DRAW_STATS:
    LDA #$48
    STA $07C2
    LDA #$50
    STA $07C3
    LDA #$3A
    STA $07C4
    LDA HP
    CLC
    ADC #$30
    STA $07C5
    LDA #$47
    STA $07CB
    LDA #$3A
    STA $07CC
    LDA GOLD
    JSR P_2D
    STX $07CD
    STA $07CE
    LDA #$52
    STA $07D4
    LDA #$3A
    STA $07D5
    LDA ROOM
    CLC
    ADC #$30
    STA $07D6
    RTS

P_2D:
    LDX #$30
P2_L:
    CMP #10
    BCC P2_D
    SEC
    SBC #10
    INX
    JMP P2_L
P2_D:
    CLC
    ADC #$30
    RTS

SET_PTR:
    LDA ROWL,X
    STA PTR_L
    LDA ROWH,X
    STA PTR_H
    RTS

SET_PTR_Y:
    LDA ROWL,Y
    STA PTR_L
    LDA ROWH,Y
    STA PTR_H
    RTS

INIT_ROWS:
    LDA #$00
    STA PTR_L
    LDA #$04
    STA PTR_H
    LDX #$00
IR_L:
    LDA PTR_L
    STA ROWL,X
    LDA PTR_H
    STA ROWH,X
    CLC
    LDA PTR_L
    ADC #$28
    STA PTR_L
    BCC IR_NC
    INC PTR_H
IR_NC:
    INX
    CPX #$19
    BNE IR_L
    RTS

QUIT:
    RTS
