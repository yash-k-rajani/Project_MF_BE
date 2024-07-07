from fastapi import (APIRouter, File, UploadFile, HTTPException, status, Query,)
from fastapi.responses import JSONResponse
from constants import constants
import os
import pandas as pd
import dask.dataframe as dd
import json


router = APIRouter(
    prefix="/file",
    tags=["FILE"]
)

@router.post(path="/upload")
async def upload(file: UploadFile = File(...)):
    save_path = os.path.join(constants.SAVE_DIR, constants.DATA_FILE_NAME)
    os.makedirs(constants.SAVE_DIR,mode=777,exist_ok=True)
    try:
        contents = await file.read()
        content_type = file.content_type

        if not (content_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file.")
        
        with open(save_path, "wb") as f:
            f.write(contents)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "File Uploaded Successfully."})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Something went wrong!!"})
    
@router.get(path="/get_details")
async def get_details(
    aum: int = Query(10),
    three_yr_rolling_rtn: int = Query(40),
    ten_yr_cagr: int = Query(5),
    cgar_five_yr: int = Query(15),
    absolute_rtn_one_yr: int = Query(5),
    lc: int = Query(10),
    mc: int = Query(7),
    sc: int = Query(3),
    pe: int = Query(10),
    std_div: int = Query(5),
    sharpe_ratio: int = Query(5),
    maximum_drawdown: int = Query(2),
    sortino_ratio: int = Query(10),
    alpha: int = Query(5),
    fund_managet: int = Query(0),
    turn_around: int = Query(0),
    time_since_inception: int = Query(20),
    number_of_rows: int = Query(10),
):
    file_path = os.path.join(constants.SAVE_DIR, constants.DATA_FILE_NAME)

    df = pd.read_excel(file_path, header=7)
    df = df.drop('group rating', axis=1)

    weights = {
        'score': aum / 100,
        'score.1': three_yr_rolling_rtn / 100,
        'score.2': cgar_five_yr / 100,
        'score.3': ten_yr_cagr / 100,
        'score.4': absolute_rtn_one_yr / 100,
        'score.5': lc / 100,
        'score.6': mc / 100,
        'score.7': sc / 100,
        'score.8': pe / 100,
        'score.9': alpha / 100,
        'score.10': sortino_ratio / 100,
        'score.11': sharpe_ratio / 100,
        'score.12': std_div / 100,
        'score.13': maximum_drawdown / 100,
        'score.14': time_since_inception / 100,
    }
    ddf = dd.from_pandas(df, npartitions=4)
    def calculate_group_rating(row, weights):
        return sum(row[score] * weight for score, weight in weights.items())
    ddf['group rating'] = ddf.apply(calculate_group_rating, axis=1, weights=weights, meta=('group rating', 'f8'))
    df_result = ddf.compute()

    df = df_result.sort_values(by=["group rating"], ascending=False)
    if number_of_rows:
        data = json.loads(df.head(number_of_rows).to_json(orient="records"))
    else:
        data = json.loads(df.to_json(orient="records"))
    return JSONResponse(status_code=status.HTTP_200_OK, content=data)