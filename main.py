import asyncio
import json

import pandas
import websockets
from pandas_ta import rsi


async def binance(uri='wss://stream.binance.com:9443/ws/btcusdt@kline_5m', length=15):
    close_list = []
    async with websockets.connect(uri) as ws:
        while True:
            response = await ws.recv()
            data = json.loads(response)['k']
            is_closed = data['x']

            if is_closed:
                on_close = float(data['c'])
                close_list.append(on_close)

                if len(close_list) > length:
                    close_list.pop(0)
                # print('close list=', close_list)
                if len(close_list) == length:
                    res = rsi(pandas.Series, length=length).tail(1).values
                    print(f'Binance \nRSI = {res[0]} \tclose price = {on_close}')


async def bitfinex(uri='wss://api-pub.bitfinex.com/ws/2',
                   request='{"event":"subscribe","channel":"candles","key":"trade:1m:tBTCUSD"}'):
    async with websockets.connect(uri) as ws:
        await ws.send(request)
        cumulative_pv: float = 0
        cumulative_volume: float = 0
        while True:
            response = await ws.recv()
            data = json.loads(response)
            if isinstance(data, list) and data[1] != 'hb':
                try:
                    on_close = float(data[1][2])
                    max = float(data[1][3])
                    min = float(data[1][4])
                    vol = float(data[1][5])
                    cumulative_volume += vol
                    typical_price = (max + min + on_close) / 3
                    cumulative_pv += typical_price * vol
                    vwap = cumulative_pv / cumulative_volume
                    print(f'Bitfinex \nVWAP = {vwap} \tclose price = {on_close}')
                except TypeError:
                    pass


async def main():
    await asyncio.gather(binance(), bitfinex())


if __name__ == '__main__':
    asyncio.run(main())
