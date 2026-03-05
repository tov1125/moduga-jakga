"""
Gemini AI 디자인 컨설팅 스크립트
4색 팔레트 기반 사이트 컬러 리디자인 HSL 값 및 접근성 검증 요청
"""

import json
import os
import sys
from pathlib import Path

# backend/.env에서 API 키 로드
from dotenv import load_dotenv

backend_env = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(backend_env)

from google import genai

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    print("ERROR: GOOGLE_API_KEY not found in backend/.env")
    sys.exit(1)

client = genai.Client(api_key=GOOGLE_API_KEY)

PROMPT = """You are an expert UI/UX designer specializing in accessible web design for visually impaired users.

## Task
Redesign a web application's color system using the following 4-color palette with the 60-30-10 rule.

## Target Application
- Name: "모두가 작가" (Everyone is an Author)
- Purpose: Web app helping visually impaired people write and publish books
- Tech: Next.js + Tailwind CSS + shadcn/ui
- Accessibility: WCAG 2.1 AA minimum, screen reader compatible
- Theme: Supports light mode and dark mode via CSS variables (HSL format)

## Color Palette (User Provided)
1. **Pure White** #FFFFFF — 60% Dominant (backgrounds)
2. **Soft Grey** #DFE6E9 — 30% Secondary (cards, sections, borders)
3. **Deep Charcoal** #2D3436 — Base text color & dark mode background
4. **Accent Gold** #D4A843 — 10% Accent (CTAs, links, highlights, focus)

## Required Output (JSON format)

Return a valid JSON object with this exact structure:

```json
{
  "css_variables": {
    "light": {
      "--background": "H S% L%",
      "--foreground": "H S% L%",
      "--card": "H S% L%",
      "--card-foreground": "H S% L%",
      "--popover": "H S% L%",
      "--popover-foreground": "H S% L%",
      "--primary": "H S% L%",
      "--primary-foreground": "H S% L%",
      "--secondary": "H S% L%",
      "--secondary-foreground": "H S% L%",
      "--muted": "H S% L%",
      "--muted-foreground": "H S% L%",
      "--accent": "H S% L%",
      "--accent-foreground": "H S% L%",
      "--destructive": "H S% L%",
      "--destructive-foreground": "H S% L%",
      "--border": "H S% L%",
      "--input": "H S% L%",
      "--ring": "H S% L%"
    },
    "dark": {
      "--background": "H S% L%",
      "--foreground": "H S% L%",
      "--card": "H S% L%",
      "--card-foreground": "H S% L%",
      "--popover": "H S% L%",
      "--popover-foreground": "H S% L%",
      "--primary": "H S% L%",
      "--primary-foreground": "H S% L%",
      "--secondary": "H S% L%",
      "--secondary-foreground": "H S% L%",
      "--muted": "H S% L%",
      "--muted-foreground": "H S% L%",
      "--accent": "H S% L%",
      "--accent-foreground": "H S% L%",
      "--destructive": "H S% L%",
      "--destructive-foreground": "H S% L%",
      "--border": "H S% L%",
      "--input": "H S% L%",
      "--ring": "H S% L%"
    }
  },
  "tailwind_scales": {
    "primary": {
      "50": "#hex", "100": "#hex", "200": "#hex", "300": "#hex",
      "400": "#hex", "500": "#hex", "600": "#hex", "700": "#hex",
      "800": "#hex", "900": "#hex", "950": "#hex"
    },
    "accent": {
      "50": "#hex", "100": "#hex", "200": "#hex", "300": "#hex",
      "400": "#hex", "500": "#hex", "600": "#hex", "700": "#hex",
      "800": "#hex", "900": "#hex", "950": "#hex"
    },
    "gray": {
      "50": "#hex", "100": "#hex", "200": "#hex", "300": "#hex",
      "400": "#hex", "500": "#hex", "600": "#hex", "700": "#hex",
      "800": "#hex", "900": "#hex", "950": "#hex"
    }
  },
  "focus_ring": {
    "light": "#hex",
    "dark": "#hex",
    "rationale": "Why this color for focus"
  },
  "contrast_ratios": {
    "charcoal_on_white": { "ratio": "X:1", "wcag_aa": true, "wcag_aaa": true },
    "gold_on_white": { "ratio": "X:1", "wcag_aa": true, "wcag_aaa": false },
    "gold_on_charcoal": { "ratio": "X:1", "wcag_aa": true, "wcag_aaa": false },
    "white_on_gold": { "ratio": "X:1", "wcag_aa": true, "wcag_aaa": false },
    "charcoal_on_grey": { "ratio": "X:1", "wcag_aa": true, "wcag_aaa": false },
    "gold_on_grey": { "ratio": "X:1", "wcag_aa": false, "wcag_aaa": false }
  },
  "component_mapping": {
    "header_bg_light": "description",
    "header_bg_dark": "description",
    "cta_button": "description",
    "secondary_button": "description",
    "card_bg_light": "description",
    "card_bg_dark": "description",
    "link_text_light": "description",
    "link_text_dark": "description",
    "selection_bg": "description"
  },
  "accessibility_notes": [
    "Note about gold on white text contrast",
    "Note about focus ring visibility",
    "Note about dark mode contrast"
  ]
}
```

## Important Rules
1. HSL values must be in shadcn/ui format: "H S% L%" (e.g., "43 55.1% 55.1%") — no "hsl()" wrapper
2. Gold (#D4A843) as primary/accent — ensure text contrast on white bg meets 4.5:1 (you may need a darker gold variant for text)
3. Focus ring must be visible on BOTH white and charcoal backgrounds (3:1 minimum)
4. Gray scale should be based on the Soft Grey (#DFE6E9) cool tone, NOT neutral gray
5. Dark mode background should be #2D3436 (Deep Charcoal), NOT pure black
6. Destructive color (red) should remain recognizable in both modes
7. All contrast ratios must be calculated accurately

Return ONLY the JSON object, no markdown fences, no extra text."""


def main():
    # Try user-requested model first, then fallback
    models_to_try = [
        "gemini-3.1-pro-preview",
    ]

    result = None
    used_model = None

    for model_name in models_to_try:
        print(f"Trying model: {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=PROMPT,
            )
            result = response.text
            used_model = model_name
            print(f"Success with model: {model_name}")
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            continue

    if result is None:
        print("ERROR: All models failed")
        sys.exit(1)

    # Clean up response (remove markdown fences if present)
    cleaned = result.strip()
    if cleaned.startswith("```"):
        # Remove first line (```json) and last line (```)
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1])

    # Parse and validate JSON
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"WARNING: JSON parsing failed: {e}")
        print("Raw response saved to redesign_result_raw.txt")
        output_raw = Path(__file__).parent / "redesign_result_raw.txt"
        output_raw.write_text(result, encoding="utf-8")
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            try:
                data = json.loads(json_match.group())
                print("Extracted JSON from response successfully")
            except json.JSONDecodeError:
                print("Could not extract valid JSON")
                sys.exit(1)
        else:
            sys.exit(1)

    # Add metadata
    data["_metadata"] = {
        "model_used": used_model,
        "palette": {
            "white": "#FFFFFF",
            "soft_grey": "#DFE6E9",
            "deep_charcoal": "#2D3436",
            "accent_gold": "#D4A843",
        },
    }

    # Save result
    output_path = Path(__file__).parent / "redesign_result.json"
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResult saved to: {output_path}")
    print(f"Model used: {used_model}")

    # Print summary
    if "contrast_ratios" in data:
        print("\n=== Contrast Ratios ===")
        for key, val in data["contrast_ratios"].items():
            ratio = val.get("ratio", "?")
            aa = "AA" if val.get("wcag_aa") else "--"
            aaa = "AAA" if val.get("wcag_aaa") else "---"
            print(f"  {key}: {ratio} [{aa}] [{aaa}]")

    if "accessibility_notes" in data:
        print("\n=== Accessibility Notes ===")
        for note in data["accessibility_notes"]:
            print(f"  - {note}")


if __name__ == "__main__":
    main()
