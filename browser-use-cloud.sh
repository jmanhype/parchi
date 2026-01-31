#!/bin/bash
# Browser Use Cloud - Quick CLI for jmanhype
# Usage: ./browser-use-cloud.sh [command]

API_KEY="bu_-RidfzaFluhAZyFRpW7WGMPawCt283uC5ckFNRaMux4"
PROFILE_ID="e20b0219-f8b5-4fce-95ad-f9fc447d3716"
PROFILE_NAME="jmanhype-main"
BASE_URL="https://api.browser-use.com/api/v2"

case "$1" in
    start|create)
        echo "🚀 Starting browser session with profile: $PROFILE_NAME"
        RESPONSE=$(curl -s -X POST "$BASE_URL/browsers" \
            -H "X-Browser-Use-API-Key: $API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"profileId\":\"$PROFILE_ID\",\"timeout\":60}")

        SESSION_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        LIVE_URL=$(echo "$RESPONSE" | grep -o '"liveUrl":"[^"]*' | cut -d'"' -f4 | sed 's/\\u0026/\&/g')

        echo ""
        echo "✅ Session started!"
        echo "   Session ID: $SESSION_ID"
        echo ""
        echo "🌐 Live Browser URL:"
        echo "   $LIVE_URL"
        echo ""
        echo "💡 To open in browser:"
        echo "   open '$LIVE_URL'"
        ;;

    list)
        echo "📋 Active browser sessions:"
        curl -s "$BASE_URL/browsers" \
            -H "X-Browser-Use-API-Key: $API_KEY" | jq -r '.[] | "\(.id) - \(.status)"'
        ;;

    stop)
        if [ -z "$2" ]; then
            echo "Usage: $0 stop <session-id>"
            exit 1
        fi
        echo "🛑 Stopping session: $2"
        curl -s -X PATCH "$BASE_URL/browsers/$2" \
            -H "X-Browser-Use-API-Key: $API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"status":"stopped"}' | jq .
        ;;

    profile)
        echo "👤 Profile info: $PROFILE_NAME"
        echo "   ID: $PROFILE_ID"
        echo ""
        curl -s "$BASE_URL/profiles" \
            -H "X-Browser-Use-API-Key: $API_KEY" | jq ".[] | select(.id==\"$PROFILE_ID\")"
        ;;

    *)
        echo "Browser Use Cloud CLI"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Commands:"
        echo "  start, create    - Start new browser session with your profile"
        echo "  list             - List active sessions"
        echo "  stop <id>        - Stop a session (refunds unused time)"
        echo "  profile          - Show profile info"
        echo ""
        echo "Example:"
        echo "  $0 start"
        ;;
esac
