# The Task

I am an indie game developer creating a multiplayer leaderboard. I want fast reads, safe writes, rollback on failures, and built-in HTTP endpoints for my game server. This code repository is my embedded JSON DB for all player and match state.

# The Requirements

* `setTTL` : Expire old match records after 24 hours, to keep the leaderboard fresh.
* `createIndex` : Index on playerID, score, and matchID for O(1) lookups and range queries.
* `encryptAtRest` : AES-256 disk encryption to prevent tampering with saved game states.
* `enforceSchema` : JSON Schema to enforce shape of player profiles, match results, and achievements.
* `registerPlugin` : Plugins for rate-limiting, custom logging, in-game analytics or replication to cloud.
* `batchUpsert` : Atomically insert/update multiple player scores or match events in one go.
* `persistAtomically` : Safe file persistence ensures partial writes during server crash don’t corrupt player data.
* `delete` : Remove abandoned player data or matches by query filters, or by explicit ID.
* `softDelete` : Flag players or matches as deleted so admins can review before permanent purge.
* `startRestServer` : Expose RESTful endpoints for game clients to post scores, query leaderboards, and administer matches.
