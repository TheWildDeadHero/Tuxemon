# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2023 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.condition.condeffect import CondEffect, CondEffectResult

if TYPE_CHECKING:
    from tuxemon.condition.condition import Condition
    from tuxemon.monster import Monster


class NoddingOffEffectResult(CondEffectResult):
    pass


@dataclass
class NoddingOffEffect(CondEffect):
    """
    This effect has a chance to apply the nodding off status effect.
    """

    name = "noddingoff"

    def apply(
        self, tech: Condition, target: Monster
    ) -> NoddingOffEffectResult:
        return {
            "success": True,
            "condition": None,
            "technique": None,
            "extra": None,
        }