from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Item rarity ─────────────────────────────────────

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


# ── Item effect types ───────────────────────────────

class EffectType(Enum):
    HEAL = "heal"
    DAMAGE = "damage"
    SPEED_BOOST = "speed_boost"
    SHIELD = "shield"
    REVEAL_MAP = "reveal_map"
    NONE = "none"


# ── Item dataclass ──

@dataclass
class Item:

    item_id: str
    name: str
    description: str = ""
    rarity: ItemRarity = ItemRarity.COMMON
    effect_type: EffectType = EffectType.NONE
    effect_value: int = 0
    consumable: bool = False
    stackable: bool = False
    weight: float = 1.0
    symbol: str = "I"

    def use(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "effect_type": self.effect_type.value,
            "effect_value": self.effect_value,
            "consumed": self.consumable,
            "message": f"Used {self.name}.",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity.value,
            "effect_type": self.effect_type.value,
            "effect_value": self.effect_value,
            "consumable": self.consumable,
            "stackable": self.stackable,
            "weight": self.weight,
            "symbol": self.symbol,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Item:
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data.get("description", ""),
            rarity=ItemRarity(data.get("rarity", "common")),
            effect_type=EffectType(data.get("effect_type", "none")),
            effect_value=int(data.get("effect_value", 0)),
            consumable=bool(data.get("consumable", False)),
            stackable=bool(data.get("stackable", False)),
            weight=float(data.get("weight", 1.0)),
            symbol=data.get("symbol", "I"),
        )


# ── Inventory slot ──────────────────────────────────

@dataclass
class InventorySlot:
    item: Item
    quantity: int = 1

    @property
    def total_weight(self) -> float:
        return self.item.weight * self.quantity

    def to_dict(self) -> dict[str, Any]:
        return {"item": self.item.to_dict(), "quantity": self.quantity}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InventorySlot:
        return cls(
            item=Item.from_dict(data["item"]),
            quantity=int(data.get("quantity", 1)),
        )


# ── Inventory ──────────────────────────────────────────────────────

@dataclass
class Inventory:

    max_slots: int = 0
    max_weight: float = 0.0
    _slots: list[InventorySlot] = field(default_factory=list, repr=False)
    _equipped: dict[str, Item] = field(default_factory=dict, repr=False)

    @property
    def items(self) -> list[str]:
        result: list[str] = []
        for slot in self._slots:
            result.extend([slot.item.name] * slot.quantity)
        return result

    # ── Weight / capacity queries ───────────────────

    @property
    def current_weight(self) -> float:
        return sum(slot.total_weight for slot in self._slots)

    @property
    def slot_count(self) -> int:
        return len(self._slots)

    @property
    def is_full(self) -> bool:
        if self.max_slots > 0 and self.slot_count >= self.max_slots:
            return True
        return False

    def would_exceed_weight(self, item: Item, quantity: int = 1) -> bool:
        if self.max_weight <= 0:
            return False
        return self.current_weight + (item.weight * quantity) > self.max_weight

    def add(self, item: Item, quantity: int = 1) -> bool:
        if self.would_exceed_weight(item, quantity):
            return False

        if item.stackable:
            for slot in self._slots:
                if slot.item.item_id == item.item_id:
                    slot.quantity += quantity
                    return True

        if self.is_full:
            return False

        self._slots.append(InventorySlot(item=item, quantity=quantity))
        return True

    def remove(self, item_id: str, quantity: int = 1) -> bool:
        for i, slot in enumerate(self._slots):
            if slot.item.item_id == item_id:
                if slot.quantity < quantity:
                    return False
                slot.quantity -= quantity
                if slot.quantity <= 0:
                    self._slots.pop(i)
                return True
        return False

    def update_item(self, old_item_id: str, new_item: Item) -> bool:

        for i, slot in enumerate(self._slots):
            if slot.item.item_id == old_item_id:
                self._slots[i] = InventorySlot(item=new_item, quantity=slot.quantity)
                return True
        return False

    def has(self, item_id: str, quantity: int = 1) -> bool:
        for slot in self._slots:
            if slot.item.item_id == item_id and slot.quantity >= quantity:
                return True
        return False

    def get_item(self, item_id: str) -> Item | None:
        for slot in self._slots:
            if slot.item.item_id == item_id:
                return slot.item
        return None

    def get_quantity(self, item_id: str) -> int:
        for slot in self._slots:
            if slot.item.item_id == item_id:
                return slot.quantity
        return 0

    # ── Use / consume ───────────────────────────────

    def use_item(self, item_id: str) -> dict[str, Any] | None:
        item = self.get_item(item_id)
        if item is None:
            return None

        result = item.use()
        if item.consumable:
            self.remove(item_id, 1)
        return result

    # ── Equip / unequip ─────────────────────────────

    def equip(self, item_id: str, slot_name: str = "main_hand") -> bool:
        item = self.get_item(item_id)
        if item is None:
            return False

        if slot_name in self._equipped:
            self.unequip(slot_name)

        self._equipped[slot_name] = item
        self.remove(item_id, 1)
        return True

    def unequip(self, slot_name: str) -> bool:
        item = self._equipped.pop(slot_name, None)
        if item is None:
            return False
        self.add(item, 1)
        return True

    def get_equipped(self, slot_name: str) -> Item | None:
        return self._equipped.get(slot_name)

    # ── Trading ─────────────────────────────────────

    def transfer_to(
        self, other: Inventory, item_id: str, quantity: int = 1
    ) -> bool:
        item = self.get_item(item_id)
        if item is None or not self.has(item_id, quantity):
            return False
        if other.would_exceed_weight(item, quantity):
            return False
        if not item.stackable and other.is_full:
            return False

        self.remove(item_id, quantity)
        other.add(item, quantity)
        return True


    def summary_lines(self) -> list[str]:
        if not self._slots:
            return ["(empty)"]
        lines: list[str] = []
        for slot in self._slots:
            qty_str = f" x{slot.quantity}" if slot.quantity > 1 else ""
            lines.append(
                f"  {slot.item.name}{qty_str} ({slot.item.rarity.value})"
            )
        return lines

    def clear(self) -> None:
        self._slots.clear()
        self._equipped.clear()

    # ── Serialization ───────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_slots": self.max_slots,
            "max_weight": self.max_weight,
            "slots": [s.to_dict() for s in self._slots],
            "equipped": {
                slot_name: item.to_dict()
                for slot_name, item in self._equipped.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Inventory:
        inv = cls(
            max_slots=int(data.get("max_slots", 0)),
            max_weight=float(data.get("max_weight", 0.0)),
        )
        inv._slots = [
            InventorySlot.from_dict(s) for s in data.get("slots", [])
        ]
        inv._equipped = {
            name: Item.from_dict(item_data)
            for name, item_data in data.get("equipped", {}).items()
        }
        return inv


# ── Pre-built item catalog ──────────────────────────

def health_potion() -> Item:
    return Item(
        item_id="health_potion",
        name="Health Potion",
        description="Restores 20 HP.",
        rarity=ItemRarity.COMMON,
        effect_type=EffectType.HEAL,
        effect_value=20,
        consumable=True,
        stackable=True,
        weight=0.5,
        symbol="P",
    )


def speed_scroll() -> Item:
    return Item(
        item_id="speed_scroll",
        name="Speed Scroll",
        description="Grants an extra move this turn.",
        rarity=ItemRarity.UNCOMMON,
        effect_type=EffectType.SPEED_BOOST,
        effect_value=1,
        consumable=True,
        stackable=True,
        weight=0.2,
        symbol="S",
    )


def shield_amulet() -> Item:
    return Item(
        item_id="shield_amulet",
        name="Shield Amulet",
        description="Blocks the next hazard encountered.",
        rarity=ItemRarity.RARE,
        effect_type=EffectType.SHIELD,
        effect_value=1,
        consumable=True,
        stackable=False,
        weight=1.0,
        symbol="A",
    )


def map_fragment() -> Item:
    return Item(
        item_id="map_fragment",
        name="Map Fragment",
        description="Reveals nearby relic locations.",
        rarity=ItemRarity.UNCOMMON,
        effect_type=EffectType.REVEAL_MAP,
        effect_value=3,
        consumable=True,
        stackable=True,
        weight=0.1,
        symbol="M",
    )


def relic_shard() -> Item:
    return Item(
        item_id="relic_shard",
        name="Relic Shard",
        description="A fragment of an ancient artifact.",
        rarity=ItemRarity.RARE,
        effect_type=EffectType.NONE,
        effect_value=0,
        consumable=False,
        stackable=True,
        weight=0.5,
        symbol="R",
    )