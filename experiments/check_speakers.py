import re
import sys
from datetime import datetime, timedelta

def parse_time(time_str):
    # Parse VTT time format: HH:MM:SS.mmm or MM:SS.mmm
    parts = time_str.replace(',', '.').split(':')
    if len(parts) == 3:
        h, m, s = parts
    else:
        h = 0
        m, s = parts
    return int(h) * 3600 + int(m) * 60 + float(s)

chapters = [
    {"time": 0, "label": "Kaspar König: Show Intro"},
    {"time": 141, "label": "Workshop Participants: The SCHAISS Workshop"},
    {"time": 330, "label": "🎶 Music (Intermezzo)"},
    {"time": 421, "label": "Pije: Anti-Capitalist Hardware"},
    {"time": 647, "label": "Gandalf & Valentina: Robots and Data Art"},
    {"time": 1011, "label": "Flo Kaufmann: Bricolage Universal"},
    {"time": 1391, "label": "🎶 Music (Intermezzo)"},
    {"time": 1417, "label": "Alwin Weber: The Simulation of Utopia"},
    {"time": 1673, "label": "Olsen: Automotive Pixel Art"},
    {"time": 2011, "label": "Oli Jäggi: The Origins of Homemade"},
    {"time": 2270, "label": "Taras: Micro-Sound & Touch-Micing"},
    {"time": 3209, "label": "Kaspar König: Outro & Credits"}
]

vtt_file = 'Clap_to_Colab3_kaspar_koenig_260818_14_colaboradio_improved.vtt'

def get_chapter(seconds):
    current_chapter = chapters[0]
    for ch in chapters:
        if seconds >= ch["time"]:
            current_chapter = ch
        else:
            break
    return current_chapter

def main():
    print(f"Reading {vtt_file}...")
    with open(vtt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Parse cues
    cues = []
    current_time = 0
    
    for i, line in enumerate(lines):
        # Match timestamp line
        time_match = re.match(r'(\d{2}:)?\d{2}:\d{2}\.\d{3}\s*-->\s*(\d{2}:)?\d{2}:\d{2}\.\d{3}', line)
        if time_match:
            start_str = line.split('-->')[0].strip()
            current_time = parse_time(start_str)
            continue
            
        # Match speaker line
        speaker_match = re.match(r'^\[(.*?)\]:\s*(.*)', line)
        if speaker_match:
            speaker = speaker_match.group(1)
            cues.append({
                'line_idx': i,
                'time': current_time,
                'speaker': speaker,
                'original': line
            })

    # Group by chapter
    chapter_speakers = {}
    for cue in cues:
        ch = get_chapter(cue['time'])
        ch_label = ch['label']
        if ch_label not in chapter_speakers:
            chapter_speakers[ch_label] = set()
        chapter_speakers[ch_label].add(cue['speaker'])

    # Present summary and interactive prompt
    print("\n--- Speaker Analysis by Chapter ---")
    
    replacements = {} # mapping (chapter_label, old_speaker) -> new_speaker

    for ch in chapters:
        label = ch['label']
        speakers = chapter_speakers.get(label, set())
        print(f"\nChapter: {label} (Starts at {ch['time']}s)")
        if not speakers:
            print("  No speakers found.")
            continue
        print(f"  Speakers: {', '.join(speakers)}")
        
        for spk in speakers:
            # Let's prompt for all speakers just in case, or only those like Speaker 1
            ans = input(f"  Rename [{spk}] in this chapter? (Enter new name, or press Enter to skip): ").strip()
            if ans:
                replacements[(label, spk)] = ans
                print(f"    -> Will rename [{spk}] to [{ans}] in {label}")

    if not replacements:
        print("\nNo renames requested. Exiting.")
        return

    # Apply replacements
    print("\nApplying replacements...")
    modified_count = 0
    for cue in cues:
        ch_label = get_chapter(cue['time'])['label']
        old_speaker = cue['speaker']
        if (ch_label, old_speaker) in replacements:
            new_speaker = replacements[(ch_label, old_speaker)]
            # Replace only the first occurrence (the speaker tag)
            old_line = lines[cue['line_idx']]
            new_line = old_line.replace(f"[{old_speaker}]:", f"[{new_speaker}]:", 1)
            lines[cue['line_idx']] = new_line
            modified_count += 1

    # Save file
    backup_file = vtt_file + '.bak'
    print(f"Saving backup to {backup_file}...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        with open(vtt_file, 'r', encoding='utf-8') as orig:
            f.write(orig.read())

    print(f"Writing updated VTT to {vtt_file}...")
    with open(vtt_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print(f"Done! Modified {modified_count} lines.")

if __name__ == '__main__':
    main()
