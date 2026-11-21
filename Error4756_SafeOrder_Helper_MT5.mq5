//+------------------------------------------------------------------+
//|                                Error4756_SafeOrder_Helper_MT5.mq5|
//|                                     AlgoEdge Systems (MohsinMQL) |
//|                     https://www.fiverr.com/mosinraza             |
//+------------------------------------------------------------------+
#property copyright "AlgoEdge Systems"
#property link      "https://www.fiverr.com/mosinraza"
#property version   "1.00"
#property description "Auto-detects broker filling mode (FOK/IOC/RETURN) and normalizes lot step to prevent MT5 Error 4756."

#include <Trade\Trade.mqh>

input string ___Support___ = "Custom MT4/MT5 EA Fixes: fiverr.com/mosinraza";
input double InpLotSize    = 0.01;
input int    InpMagic      = 475601;

CTrade trade;

ENUM_ORDER_TYPE_FILLING DetectFillingMode(const string sym)
{
   uint filling = (uint)SymbolInfoInteger(sym, SYMBOL_FILLING_MODE);
   if((filling & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK)
      return ORDER_FILLING_FOK;
   if((filling & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC)
      return ORDER_FILLING_IOC;
   return ORDER_FILLING_RETURN;
}

double NormalizeLots(const string sym, double lots)
{
   double minLot  = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   double stepLot = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   if(stepLot <= 0.0) stepLot = 0.01;
   lots = MathMax(minLot, MathMin(maxLot, MathFloor(lots / stepLot) * stepLot));
   return NormalizeDouble(lots, 2);
}

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetTypeFilling(DetectFillingMode(_Symbol));
   Print("AlgoEdge SafeOrder Helper initialized | Symbol: ", _Symbol,
         " | Filling Mode: ", EnumToString(DetectFillingMode(_Symbol)),
         " | Normalized Lot: ", NormalizeLots(_Symbol, InpLotSize));
   return INIT_SUCCEEDED;
}

void OnTick()
{
   // Attach this template's DetectFillingMode() & NormalizeLots() inside your EA
   // before calling trade.Buy() / trade.Sell() to eliminate MT5 Error 4756.
}
//+------------------------------------------------------------------+
