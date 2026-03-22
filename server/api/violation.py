# -*- coding: utf-8 -*-
"""
Violation report API — receives violation data from the desktop client
and forwards it to a Feishu (Lark) group webhook as a rich-text card.

Author : AHDUNYI
Version: 1.0.0
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

import requests
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger("ahdunyi")

router = APIRouter(tags=["violation"])

FEISHU_WEBHOOK_URL: str = os.environ.get(
    "FEISHU_WEBHOOK_URL",
    "https://open.feishu.cn/open-apis/bot/v2/hook/3f74a5ed-3f34-4162-886d-3d39b29f3019",
)

ACTION_LABELS: dict[str, str] = {
    "ban": "封禁",
    "mute": "禁言",
    "close_room": "关播",
}


class ViolationReport(BaseModel):
    room_id: str = ""
    user_id: str = ""
    reason: str
    action: str  # ban | mute | close_room
    operator: str = ""
    timestamp: str = ""


class ReportResponse(BaseModel):
    success: bool
    message: str


@router.post("/api/violation/report", response_model=ReportResponse)
def report_violation(body: ViolationReport) -> ReportResponse:
    """Receive a violation report and forward to Feishu webhook."""

    action_label = ACTION_LABELS.get(body.action, body.action)
    ts = body.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🚨 直播违规处置通知",
                },
                "template": "red",
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**房间号**\n{body.room_id or '未知'}",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**违规主播ID**\n{body.user_id or '未知'}",
                            },
                        },
                    ],
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**违规原因**\n{body.reason}",
                    },
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**处罚动作**\n🔴 {action_label}",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**操作人**\n{body.operator or '未知'}",
                            },
                        },
                    ],
                },
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"HuiInsight 徽鉴 · {ts}",
                        },
                    ],
                },
            ],
        },
    }

    try:
        resp = requests.post(
            FEISHU_WEBHOOK_URL,
            json=card,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        resp_data = resp.json()
        logger.info(
            "Feishu webhook response: %s (room=%s, user=%s, action=%s)",
            resp_data, body.room_id, body.user_id, body.action,
        )

        if resp_data.get("code") == 0 or resp_data.get("StatusCode") == 0:
            return ReportResponse(success=True, message="违规通知已发送到飞书群")

        return ReportResponse(
            success=False,
            message=f"飞书返回错误: {resp_data.get('msg', '未知')}",
        )

    except requests.RequestException as exc:
        logger.error("Feishu webhook failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"飞书通知发送失败: {exc}",
        ) from exc
