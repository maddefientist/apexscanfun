# Legend text for explaining chart indicators and patterns

LEGEND_TEXT = """
*SPL Token Chart Legend*

*Candlestick Chart*
- Green candle: Price closed higher than it opened
- Red candle: Price closed lower than it opened
- Wicks: Show the high and low prices during the period

*Technical Indicators*
- *RSI (Relative Strength Index)*: Measures momentum and indicates overbought (>70) or oversold (<30) conditions
- *MACD (Moving Average Convergence Divergence)*: Trend-following momentum indicator showing relationship between two moving averages
  - MACD Line: Difference between 12 and 26-period EMAs
  - Signal Line: 9-period EMA of MACD Line
  - Histogram: Difference between MACD and Signal lines

*Support & Resistance*
- *Support Levels* (Green): Price levels where buying pressure tends to overcome selling pressure
- *Resistance Levels* (Red): Price levels where selling pressure tends to overcome buying pressure

*Volume*
- Bar height represents trading volume for each period
- Higher volume often confirms strength of price movements

*Common Patterns*
- *Double Top/Bottom*: Reversal patterns indicating potential trend change
- *Head & Shoulders*: Reversal pattern with three peaks, middle one highest
- *Bull/Bear Flags*: Continuation patterns after strong moves
- *Triangles*: Consolidation patterns (ascending, descending, symmetrical)

Use `/chart <token_address>` to generate a chart with these indicators.
"""