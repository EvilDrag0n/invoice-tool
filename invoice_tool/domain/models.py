from dataclasses import dataclass

@dataclass(frozen=True)
class InvoiceRecord:
    """
    Represents a normalized invoice record with exactly 10 fields.
    Fields are ordered as per the agreed Excel export schema.
    """
    文件名: str
    发票号码: str
    开票日期: str
    购买方名称: str
    购买方税号: str
    销售方名称: str
    销售方税号: str
    金额: str  # Normalized decimal string
    税额: str  # Normalized decimal string
    价税合计: str  # Normalized decimal string
    是否完整: bool = True
    缺失字段: tuple[str, ...] = ()

    def to_dict(self):
        return {
            "文件名": self.文件名,
            "发票号码": self.发票号码,
            "开票日期": self.开票日期,
            "购买方名称": self.购买方名称,
            "购买方税号": self.购买方税号,
            "销售方名称": self.销售方名称,
            "销售方税号": self.销售方税号,
            "金额": self.金额,
            "税额": self.税额,
            "价税合计": self.价税合计,
        }
