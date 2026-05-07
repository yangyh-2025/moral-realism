"""
CINC数据查询API
提供CINC（Composite Index of National Capability）数据库的查询接口
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.core.cinc_data_loader import get_cinc_loader

router = APIRouter(prefix="/cinc", tags=["CINC数据"])


@router.get("/countries", summary="获取CINC国家列表")
async def get_cinc_countries() -> List[dict]:
    """获取CINC数据库中所有国家的列表"""
    loader = get_cinc_loader()
    return loader.get_available_countries()


@router.get("/years", summary="获取CINC可用年份")
async def get_cinc_years() -> List[int]:
    """获取CINC数据库中所有可用年份"""
    loader = get_cinc_loader()
    return loader.get_available_years()


@router.get("/data", summary="按国家和年份获取CINC数据")
async def get_cinc_data(
    country_code: Optional[int] = Query(None, description="COW国家数字代码"),
    stateabb: Optional[str] = Query(None, description="国家英文缩写（如USA）"),
    year: int = Query(..., description="年份")
) -> dict:
    """按国家代码或缩写+年份获取CINC数据"""
    loader = get_cinc_loader()
    if country_code is not None:
        record = loader.get_record(country_code, year)
    elif stateabb is not None:
        record = loader.get_record_by_abb(stateabb, year)
    else:
        raise HTTPException(400, "必须提供 country_code 或 stateabb")
    if record is None:
        raise HTTPException(404, "未找到对应的CINC数据")
    return {
        "ccode": record.ccode,
        "stateabb": record.stateabb,
        "year": record.year,
        "milex": record.milex,
        "milper": record.milper,
        "irst": record.irst,
        "pec": record.pec,
        "tpop": record.tpop,
        "upop": record.upop,
        "cinc": record.cinc,
        "country_name": loader.get_country_name(record.ccode),
    }


@router.get("/by-year/{year}", summary="获取某年所有国家的CINC数据")
async def get_cinc_by_year(year: int) -> List[dict]:
    """获取指定年份所有国家的CINC数据，按CINC降序"""
    loader = get_cinc_loader()
    return loader.get_countries_by_year(year)
