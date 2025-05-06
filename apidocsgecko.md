GeckoTerminal API: Developer Cheat Sheet
🔗 API Base URL
arduino
Copy
Edit
https://api.geckoterminal.com/api/v2
📌 Key Concepts
Network ID: Identifier for the blockchain network (e.g., solana, eth).

Token Address: The SPL token's base58 address on Solana.

Pool Address: Address of the liquidity pool where the token is traded.

OHLCV Data: Open, High, Low, Close, Volume data for candlestick charts.

🔍 Core Endpoints
1. List Supported Networks
Retrieve all supported blockchain networks.

Endpoint: /networks

Method: GET

Example:

bash
Copy
Edit
GET /networks
2. Get Top Pools for a Token
Fetch top liquidity pools for a specific token on a network.

Endpoint: /networks/{network}/tokens/{token_address}/pools

Method: GET

Parameters:

network: e.g., solana

token_address: SPL token address

Example:

bash
Copy
Edit
GET /networks/solana/tokens/{token_address}/pools
3. Retrieve OHLCV Data for a Pool
Obtain historical candlestick data for a specific pool.

Endpoint: /networks/{network}/pools/{pool_address}/ohlcv/{timeframe}

Method: GET

Parameters:

network: e.g., solana

pool_address: Address of the liquidity pool

timeframe: minute, hour, or day

Query Parameters:

aggregate: Number of units to aggregate (e.g., 1, 5, 15)

before_timestamp: Unix timestamp in seconds

limit: Number of data points to return (max: 1000)

currency: usd or token (default: usd)

token: base or quote (default: base)

Example:

bash
Copy
Edit
GET /networks/solana/pools/{pool_address}/ohlcv/hour?aggregate=1&limit=100
⚠️ Rate Limits
Free Tier: 30 API calls per minute.

Higher Limits: Available through CoinGecko's paid plans.

🛠️ Implementation Tips
Selecting the Right Pool: When multiple pools exist for a token, choose the one with the highest liquidity and trading volume.

Handling Timestamps: Use Unix timestamps in seconds for before_timestamp.

Data Aggregation: Adjust the aggregate parameter to control the granularity of OHLCV data.

Error Handling: Implement robust error handling for API responses, considering rate limits and potential data inconsistencies.

🧪 Example Workflow for /chart <token_address>
User Input: /chart <token_address>

Fetch Top Pools: Use the /networks/solana/tokens/{token_address}/pools endpoint to retrieve pools.

Select Pool: Choose the pool with the highest liquidity.

Retrieve OHLCV Data: Use the /networks/solana/pools/{pool_address}/ohlcv/hour endpoint to get historical data.

Generate Chart: Plot the OHLCV data using a charting library (e.g., matplotlib, mplfinance).

Respond to User: Send the generated chart image back to the user in Telegram.

📚 Additional Resources
Official API Documentation: GeckoTerminal API Docs

Python Wrapper: geckoterminal-api on PyPI

GitHub Repository: dineshpinto/geckoterminal-api
