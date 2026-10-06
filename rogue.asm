PX = $30
PY = $31
HP   = $54
DMG  = $55
RDMG = $56
RNG  = $57
SPD  = $58
TCNT = $59
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
RCNT = $3F

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
EXIT_X = $4E
EXIT_Y = $4F
POS_X  = $52
POS_Y  = $53

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
    LDA $FE
    BNE SEED_OK
    LDA #$35
SEED_OK:
    STA SEED
    LDX #$12
SHOW:
    LDA MENU,X
    STA $07C0,X
    DEX
    BPL SHOW
WAIT_KEY:
    INC SEED
    LDA KEYBOARD
    BEQ WAIT_KEY
    LDX #$00
    STX KEYBOARD
    SEC
    SBC #$31
    CMP #$04
    BCS WAIT_KEY
    STA TCNT
    ASL
    ASL
    ADC TCNT
    TAY
    LDX #$00
CP:
    LDA CLASSTAB,Y
    STA HP,X
    INY
    INX
    CPX #$05
    BNE CP

LOAD:
    LDA #$02
    STA PX
    STA PY
    JSR GEN_ROOM
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
    CMP #$20
    BEQ FIRE
NOKEY:
    JMP INPUT
FIRE:
    LDX #M1_TYPE
    JSR CHK_RNG
    BCC F_GO
    LDX #M2_TYPE
    JSR CHK_RNG
    BCS NOKEY
F_GO:
    LDA RDMG
    JSR ATK
    JMP TURN

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
    LDA TGT_X
    CMP GOLD_X
    BNE GOLD_IS_2
    LDA TGT_Y
    CMP GOLD_Y
    BNE GOLD_IS_2
    LDA #$00
    STA GOLD_X
    STA GOLD_Y
    LDA #$02
    JSR ADD_G
    DEC G_CNT
    JMP GOLD_MOVE
GOLD_IS_2:
    LDA #$00
    STA GOLD_X2
    STA GOLD_Y2
    LDA #$02
    JSR ADD_G
    DEC G_CNT
GOLD_MOVE:
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
    CMP #$0A
    BNE LOAD
    JMP WIN

TURN:
    LDA SPD
    STA TCNT
TN:
    JSR PROC_MONS
    DEC TCNT
    BNE TN
    LDA HP
    BNE LOOP
    JMP LOSE

ATK_M1:
    LDA DMG
    LDX #M1_TYPE
    BNE ATK
ATK_M2:
    LDA DMG
    LDX #M2_TYPE
    BNE ATK
ATK:
    STA TCNT
    JSR RAND
    AND #$03
    BEQ A_RET
    LDA $03,X
    SEC
    SBC TCNT
    STA $03,X
    BEQ A_DIE
    BCS A_RET
A_DIE:
    LDA $00,X
    JSR REWARD
    LDA #$00
    STA $00,X
A_RET:
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
    LDX #M1_TYPE
    JSR MON_ATK
    LDX M1_X
    LDY M1_Y
    JSR STEP_M
    STX M1_X
    STY M1_Y

PM2:
    LDA M2_TYPE
    BEQ PM_D
    LDX #M2_TYPE
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
    CMP PX
    BNE SM_NO_PLAYER
    LDA MON_Y
    CMP PY
    BEQ SM_FAIL
SM_NO_PLAYER:
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
SM_OK:
    LDX MON_X
    LDY MON_Y
    RTS

SM_FAIL:
    LDX PTR_L
    LDY PTR_H
    RTS

MON_ATK:
    JSR DIST
    CMP #$02
    BCS MA_DONE
    LDA HP
    BEQ MA_DONE
    DEC HP
MA_DONE:
    RTS

DIST:
    LDA PX
    SEC
    SBC $01,X
    BPL D1
    EOR #$FF
    ADC #$01
D1:
    STA PTR_L
    LDA PY
    SEC
    SBC $02,X
    BPL D2
    EOR #$FF
    ADC #$01
D2:
    CLC
    ADC PTR_L
    RTS

CHK_RNG:
    LDA $00,X
    SEC
    BEQ CR_RET
    JSR DIST
    CMP RNG
CR_RET:
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
    LDA #$00
    STA M1_TYPE
    STA M1_X
    STA M2_TYPE
    STA M2_X
    STA GOLD_X
    STA GOLD_X2
    STA G_CNT
    STA M_CNT
    LDA ROOM_W
    SEC
    SBC #1
    STA EXIT_X
    LDA ROOM_H
    SEC
    SBC #1
    STA EXIT_Y
    RTS

SPAWN_GOLD:
    JSR RAND
    AND #$03
    BEQ SG_DONE
    CMP #$03
    BEQ SG_DONE
    STA G_CNT
    JSR PICK_POS
    STA GOLD_X
    STY GOLD_Y
    LDA G_CNT
    CMP #$02
    BCC SG_DONE
    JSR PICK_POS
    STA GOLD_X2
    STY GOLD_Y2
SG_DONE:
    RTS

SPAWN_MONS:
    JSR RAND
    AND #$03
    BEQ SM_NONE
    CMP #$04
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
    JSR PICK_TYPE
    STA M1_TYPE
    STY M1_HP
    JSR PICK_POS
    STA M1_X
    STY M1_Y
    RTS

SPAWN_M2:
    JSR PICK_TYPE
    STA M2_TYPE
    STY M2_HP
    JSR PICK_POS
    STA M2_X
    STY M2_Y
    RTS

PICK_POS:
PP_RETRY:
    JSR RAND
    AND #$1F
    CMP ROOM_W
    BCS PP_RETRY
    CMP #$02
    BCC PP_RETRY
    STA POS_X
    JSR RAND
    AND #$0F
    CMP ROOM_H
    BCS PP_RETRY
    CMP #$02
    BCC PP_RETRY
    STA POS_Y
    LDX #PX
    JSR CHK_AT
    BCS PP_RETRY
    LDX #EXIT_X
    JSR CHK_AT
    BCS PP_RETRY
    LDX #GOLD_X
    JSR CHK_AT
    BCS PP_RETRY
    LDX #GOLD_X2
    JSR CHK_AT
    BCS PP_RETRY
    LDX #M1_X
    JSR CHK_AT
    BCS PP_RETRY
    LDX #M2_X
    JSR CHK_AT
    BCS PP_RETRY
    LDA POS_X
    LDY POS_Y
    RTS

CHK_AT:
    LDA POS_X
    CMP $00,X
    BNE CA_FREE
    LDA POS_Y
    CMP $01,X
    BNE CA_FREE
    SEC
    RTS
CA_FREE:
    CLC
    RTS

PICK_TYPE:
    JSR RAND
    AND #$03
    TAX
    LDA #$5A
    LDY #$02
    CPX #$01
    BNE PT_1
    LDA #$53
PT_1:
    CPX #$02
    BNE PT_2
    LDA #$47
    LDY #$04
PT_2:
    RTS

RAND:
    LDA #$08
    STA RCNT
    LDA SEED
    BNE R_LOOP
    LDA #$A5
R_LOOP:
    ASL
    BCC R_NX
    EOR #$1D
R_NX:
    DEC RCNT
    BNE R_LOOP
    STA SEED
    RTS

CLS:
    LDX #$00
    LDA #$20
DM_C:
    STA $0400,X
    STA $0500,X
    STA $0600,X
    STA $0700,X
    INX
    BNE DM_C
    RTS

DRAW_MAP:
    JSR CLS
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
    LDY ROOM_H
    JSR SET_PTR_Y
    LDY ROOM_W
    LDA #$23
    STA (PTR_L),Y
    RTS

DRAW_FEAT:
    LDX EXIT_Y
    JSR SET_PTR
    LDA #$45
    LDY EXIT_X
    STA (PTR_L),Y
    LDA GOLD_X
    BEQ DF_G2
    LDX GOLD_Y
    JSR SET_PTR
    LDA #$24
    LDY GOLD_X
    STA (PTR_L),Y
DF_G2:
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
    JSR P_2D
    STX $07C5
    STA $07C6
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

LOSE:
    JSR CLS
    LDX #$08
L1:
    LDA T_OVER,X
    STA $05EF,X
    DEX
    BPL L1
    JMP END_WAIT

WIN:
    JSR CLS
    LDX #$07
W1:
    LDA T_WIN,X
    STA $05C8,X
    DEX
    BPL W1
    LDX #$0C
W2:
    LDA T_SC,X
    STA $0615,X
    DEX
    BPL W2
    LDA GOLD
    JSR P_2D
    STX $061A
    STA $061B
    LDA HP
    JSR P_2D
    STX $0620
    STA $0621
    JMP END_WAIT

END_WAIT:
    LDA #$00
    STA KEYBOARD
EW:
    LDA KEYBOARD
    BEQ EW
    LDA #$00
    STA KEYBOARD
    RTS

CLASSTAB:
    .BYTE $0A,$01,$01,$05,$01   ; ranger
    .BYTE $14,$03,$00,$00,$03   ; barbarian
    .BYTE $0F,$01,$00,$00,$01   ; fighter
    .BYTE $05,$01,$03,$09,$02   ; wizard
MENU:
    .BYTE $31,$52,$41,$4E,$20,$32,$42,$41,$52,$20
    .BYTE $33,$46,$49,$47,$20,$34,$57,$49,$5A
T_OVER:
    .BYTE $47,$41,$4D,$45,$20,$4F,$56,$45,$52
T_WIN:
    .BYTE $59,$4F,$55,$20,$57,$49,$4E,$21
T_SC:
    .BYTE $47,$4F,$4C,$44,$3A,$30,$30,$20,$48,$50,$3A,$30,$30
