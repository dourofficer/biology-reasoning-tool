DOC_URL="https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"
PROMPT="Summarize this document"
DISPLAY_NAME="base64_pdf"
GOOGLE_API_KEY="GOOGLE_API_KEY"

# Check for FreeBSD base64 and set flags accordingly
if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

# Base64 encode the PDF
ENCODED_PDF=$(base64 $B64FLAGS "${DISPLAY_NAME}.pdf")

# Create temporary JSON file
TEMP_JSON=$(mktemp)
cat > "$TEMP_JSON" <<EOF
{
  "contents": [{
    "parts":[
      {"inline_data": {"mime_type": "application/pdf", "data": "$ENCODED_PDF"}},
      {"text": "$PROMPT"}
    ]
  }]
}
EOF

# Send request using the file
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -d @"$TEMP_JSON"

# Cleanup
rm "$TEMP_JSON"