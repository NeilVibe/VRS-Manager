"""
VRS Manager Configuration
Contains all constants and configuration settings
"""

# ===========================================================================
# COLUMN NAMES
# ===========================================================================
COL_SEQUENCE = "SequenceName"
COL_EVENTNAME = "EventName"
COL_STRORIGIN = "StrOrigin"
COL_DESC = "Desc"
COL_STARTFRAME = "StartFrame"
COL_ENDFRAME = "EndFrame"
COL_TEXT = "Text"
COL_STATUS = "STATUS"
COL_FREEMEMO = "FREEMEMO"
COL_CHARACTERKEY = "CharacterKey"
COL_CHARACTERNAME = "CharacterName"
COL_DIALOGVOICE = "DialogVoice"
COL_SPEAKER_GROUPKEY = "Speaker|CharacterGroupKey"
COL_CASTINGKEY = "CastingKey"
COL_PREVIOUSDATA = "PreviousData"
COL_MAINLINE_TRANSLATION = "Mainline Translation"
COL_PREVIOUS_STRORIGIN = "Previous StrOrigin"
COL_IMPORTANCE = "Importance"
COL_DIALOGTYPE = "DialogType"
COL_GROUP = "Group"

# Phase 4 new columns
COL_CHANGES = "CHANGES"
COL_DETAILED_CHANGES = "DETAILED_CHANGES"
COL_PREVIOUS_EVENTNAME = "PreviousEventName"
COL_PREVIOUS_TEXT = "PreviousText"

# ===========================================================================
# CHARACTER GROUP COLUMNS
# ===========================================================================
CHAR_GROUP_COLS = ["Tribe", "Age", "Gender", "Job", "Region"]

# ===========================================================================
# STATUS CATEGORIES
# ===========================================================================
AFTER_RECORDING_STATUSES = {
    "RECORDED", "PREVIOUSLY RECORDED", "FINAL", "RE-RECORD", "RE-RECORDED",
    "RERECORD", "RERECORDED", "SHIPPED",
    "전달 완료", "녹음 완료", "재녹음 필요", "재녹음 완료",
    "已传达", "已录音", "需补录", "已补录",
}

PRE_RECORDING_STATUSES = {
    "", "POLISHED", "SPEC-OUT", "CHECK",
    "준비 중", "확인 필요",
    "准备中", "需要确认",
}

# ===========================================================================
# OUTPUT COLUMN STRUCTURES
# ===========================================================================
# Phase 4: CHANGES = priority label, DETAILED_CHANGES = full composite (far right)
#          PreviousText, PreviousEventName also on far right
OUTPUT_COLUMNS = [
    "DialogType", "Group", "SequenceName", "CharacterName", "CharacterKey",
    "DialogVoice", "CastingKey", "StrOrigin", "STATUS", "Text", "Desc",
    "FREEMEMO", "SubTimelineName", "CHANGES", "EventName", "StartFrame",
    "EndFrame", "Tribe", "Age", "Gender", "Job", "Region", "UpdateTime",
    "PreviousData", "PreviousText", "PreviousEventName", "DETAILED_CHANGES",
    "Previous StrOrigin", "Mainline Translation"
]

OUTPUT_COLUMNS_RAW = [
    "DialogType", "Group", "SequenceName", "CharacterName", "CharacterKey",
    "DialogVoice", "CastingKey", "StrOrigin", "STATUS", "Text", "Desc",
    "FREEMEMO", "SubTimelineName", "CHANGES", "EventName", "StartFrame",
    "EndFrame", "Tribe", "Age", "Gender", "Job", "Region", "UpdateTime",
    "PreviousData", "PreviousText", "PreviousEventName", "DETAILED_CHANGES",
    "Previous StrOrigin"
]

OUTPUT_COLUMNS_MASTER = [
    "DialogType", "Group", "SequenceName",
    "CharacterName_KR", "CharacterName_EN", "CharacterName_CN",
    "CharacterKey", "DialogVoice", "CastingKey", "StrOrigin",
    "STATUS_KR", "STATUS_EN", "STATUS_CN",
    "Text_KR", "Text_EN", "Text_CN",
    "FREEMEMO_KR", "FREEMEMO_EN", "FREEMEMO_CN",
    "SubTimelineName", "CHANGES", "EventName", "StartFrame", "EndFrame",
    "Tribe", "Age", "Gender", "Job", "Region", "UpdateTime",
    "PreviousData_KR", "PreviousData_EN", "PreviousData_CN",
    "PreviousText", "PreviousEventName", "DETAILED_CHANGES",
    "Mainline Translation_KR", "Mainline Translation_EN", "Mainline Translation_CN"
]

# ===========================================================================
# HISTORY FILES
# ===========================================================================
WORKING_HISTORY_FILE = "working_update_history.json"
MASTER_HISTORY_FILE = "master_update_history.json"
ALLLANG_HISTORY_FILE = "alllang_update_history.json"

# ===========================================================================
# VERSION INFORMATION
# ===========================================================================
VERSION = "12031417"
VERSION_FOOTER = "ver. 12031417 | 10-Key TWO-PASS Algorithm | Word-Level Diff Analysis"
