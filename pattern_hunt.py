# pattern_hunt.py
# ITSS/OPRE 3312 - Lecture 5: "Pattern Hunters"
# Squad Lab: Operation Tip Line. Mine 24 free-text tips for phones,
# dates, case refs, and beats, then count the leads with no callback.

# The "re" module is Python's built-in regular-expression library.
# We need it to search free text that has no | delimiters to split on.
import re


# ----- EXTRACTOR FUNCTIONS -----
# Each function below takes ONE argument (the tip text) and RETURNS a
# list of matches. re.findall(pattern, text) scans the whole string and
# hands back every piece that matches the pattern, as a list.
#
# SCOPE NOTE: the parameter "text" and the variable the function creates
# only exist WHILE the function is running. Nothing leaks out except what
# we hand back with "return". That is what makes these functions safe to
# reuse on 24 different tips without them stepping on each other.

def extract_phones(text):
    """Find every phone number: (214) 555-1234 or 214-555-1234."""
    # \(\d{3}\)      -> a real "(214)" style area code (parens are a pair)
    # [ -]?          -> an optional space or dash after the area code
    # \d{3}-\d{4}    -> the rest of the number, e.g. "555-1234"
    # |              -> OR match this instead:
    # \d{3}-\d{3}-\d{4} -> the plain dash-only style, e.g. "214-555-1234"
    #
    # We match the parens as a PAIR on purpose. A looser pattern like
    # \(?\d{3}\)? would also grab the "(" from a sentence like
    # "Witness (784-550-8605) reports..." where the parens belong to the
    # sentence, not the phone number.
    pattern = r"\(\d{3}\)[ -]?\d{3}-\d{4}|\d{3}-\d{3}-\d{4}"
    return re.findall(pattern, text)


def extract_case_refs(text):
    """Find every case reference, e.g. CC-14589."""
    # CC-     -> the literal letters "CC-"
    # \d{5}   -> exactly five digits after it
    pattern = r"CC-\d{5}"
    return re.findall(pattern, text)


def extract_beats(text):
    """Find every beat number mentioned, e.g. 'beat 341' -> '341'."""
    # [Bb]eat  -> the word "beat" or "Beat"
    # (space)  -> one literal space
    # (\d{3})  -> capture just the 3-digit number in parentheses, so
    #             findall returns "341" instead of "beat 341"
    pattern = r"[Bb]eat (\d{3})"
    return re.findall(pattern, text)


def extract_iso_dates(text):
    """Find every ISO-format date, e.g. 2019-02-19 (year-month-day)."""
    # \d{4}  -> four digits (the year)
    # -      -> a literal dash
    # \d{2}  -> two digits (the month)
    # -      -> a literal dash
    # \d{2}  -> two digits (the day)
    pattern = r"\d{4}-\d{2}-\d{2}"
    return re.findall(pattern, text)


def extract_us_dates(text):
    """Find every US numeric date, e.g. 4/7/2019 (month/day/year)."""
    # \d{1,2}  -> one OR two digits (the month, e.g. "4" or "12")
    # /        -> a literal slash
    # \d{1,2}  -> one OR two digits (the day)
    # /        -> a literal slash
    # \d{4}    -> four digits (the year)
    pattern = r"\d{1,2}/\d{1,2}/\d{4}"
    return re.findall(pattern, text)


def summarize_tip(tip_num, text):
    """Run every extractor on one tip and return (summary_line, has_callback).

    tip_num and text are PARAMETERS. They only exist inside this function
    while it runs (that's "scope"). Every variable we create below --
    phones, case_refs, beats, dates, has_callback -- is LOCAL to this
    function too. The only way any of that data gets out is through the
    "return" statement at the bottom.
    """
    phones = extract_phones(text)
    case_refs = extract_case_refs(text)
    beats = extract_beats(text)

    # A tip has at most one real date, but it could be written in either
    # numeric format, so we just combine both lists.
    dates = extract_iso_dates(text) + extract_us_dates(text)

    # A tip counts as having a callback if we found at least one phone
    # number in it.
    has_callback = len(phones) >= 1

    summary_line = (
        f"TIP {tip_num:>2}: phones={phones} dates={dates} "
        f"case_refs={case_refs} beats={beats} "
        f"callback={'YES' if has_callback else 'NO'}"
    )

    # Hand both pieces of evidence back to whoever called this function.
    return summary_line, has_callback


# ----- MAIN SCRIPT -----
# Everything below this line is NOT inside a function, so it runs top to
# bottom once, right when the file is executed.

# Step 1: set up the accumulators BEFORE the loop starts (slide 7's rule:
# set up before, update inside, report after). These are the only
# variables that need to survive across every tip.
tips_processed = 0
tips_with_callback = 0
tips_without_callback = 0

# Step 2: open the tip-line data and loop over it, one tip (one line) at
# a time.
data_file = open("data/wk05_data_tipline.txt")

for line in data_file:

    # Strip the trailing newline/whitespace off the line first.
    line = line.strip()

    # Skip blank lines instead of crashing on them.
    if line == "":
        continue

    tips_processed += 1

    # Call our function. summarize_tip runs with its own local variables
    # and hands back exactly two things, which we unpack here.
    summary_line, has_callback = summarize_tip(tips_processed, line)
    print(summary_line)

    if has_callback:
        tips_with_callback += 1
    else:
        tips_without_callback += 1

data_file.close()

# Step 3: report the totals AFTER the loop is done.
print()
print("----- TIP LINE REPORT -----")
print(f"Tips processed:        {tips_processed}")
print(f"Tips with a callback:  {tips_with_callback}")
print(f"Tips with NO callback: {tips_without_callback}  <- these leads die without follow-up")
