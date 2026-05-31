
with open('src/ui/gotchi_ui.py', 'r') as f:
    lines = f.readlines()

# Find the start index: "            # Wrap text with fallback awareness"
# Find the end index: "            gpio_released = True" after print(f"Simulator updated...

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "# Wrap text with fallback awareness" in line and start_idx == -1:
        start_idx = i
    if "print(f\"Simulator updated: {sim_path}\")" in line:
        end_idx = i + 1  # includes the gpio_released = True line

if start_idx != -1 and end_idx != -1:
    new_code = """            # Wrap text with fallback awareness
            all_lines = get_wrapped_text(speech_text, font_bubble, font_emoji_bubble, max_bubble_width)
            
            line_height = 18
            max_y = HEIGHT - FOOTER_H - 2
            min_y = HEADER_H + 2
            max_available_height = max_y - min_y
            max_lines_per_page = (max_available_height - 10) // line_height
            if max_lines_per_page < 1: max_lines_per_page = 1
            
            pages = [all_lines[i:i + max_lines_per_page] for i in range(0, len(all_lines), max_lines_per_page)]
            if not pages:
                pages = [[]]
            
            base_image = image.copy()
            import time
            
            for page_idx, page_lines in enumerate(pages):
                page_image = base_image.copy()
                draw = ImageDraw.Draw(page_image)
                
                # Append pagination info if needed
                if len(pages) > 1:
                    page_indicator = f" [{page_idx + 1}/{len(pages)}]"
                    if len(page_lines) > 0:
                        page_lines[-1] = page_lines[-1] + page_indicator
                    else:
                        page_lines.append(page_indicator)

                # Calculate Bubble Size with fallback awareness
                max_line_w = 0
                for line in page_lines:
                    w = get_text_width(line, font_bubble, font_emoji_bubble)
                    if w > max_line_w: max_line_w = w
                
                text_block_h = len(page_lines) * line_height
                
                bw = max_line_w + 12
                bh = text_block_h + 10
                
                # HARD CAP: Bubble cannot be wider than screen
                if bw > WIDTH - 4: bw = WIDTH - 4
                
                bx = start_x
                
                # If bubble extends beyond right edge, shift it left
                if bx + bw > WIDTH - 2:
                    bx = WIDTH - bw - 2
                
                # Vertical Align
                bubble_cy = face_y + 10 
                by = bubble_cy - bh // 2
                
                # 1. Check Header collision (Top)
                if by < HEADER_H + 2: 
                    by = HEADER_H + 2
                    
                # 2. Check Footer collision (Bottom)
                max_y = HEIGHT - FOOTER_H - 2
                if by + bh > max_y:
                    by = max_y - bh 
                    # Double check Top
                    if by < HEADER_H + 2:
                         by = HEADER_H + 2 
                
                # Draw Box
                draw.rectangle((bx, by, bx+bw, by+bh), outline=0, fill=255)
                
                # Tail (Side style)
                p_tip = (cx + fw//2 + 2, face_y + 10) # Face cheek
                
                # Base logic
                tail_y = by + bh // 2
                if tail_y > by + bh - 5: tail_y = by + bh - 5
                if tail_y < by + 5: tail_y = by + 5
                
                p_top = (bx, tail_y - 5)
                p_bot = (bx, tail_y + 5)
                
                draw.polygon([p_tip, p_top, p_bot], outline=0, fill=255)
                draw.line((bx, p_top[1] + 1, bx, p_bot[1] - 1), fill=255) 
    
                # Draw Text Lines
                curr_y = by + 5
                for line in page_lines:
                    draw_text_with_fallback(draw, (bx + 6, curr_y), line, font=font_bubble, fallback_font=font_emoji_bubble, fill=0)
                    curr_y += line_height
                
                # --- Update Display per Page ---
                rotated_image = page_image.rotate(180)
                if EPD_DRIVER_LOADED:
                    if fast_mode and page_idx == 0:
                        epd.displayPartBaseImage(epd.getbuffer(rotated_image))
                    else:
                        epd.display(epd.getbuffer(rotated_image))
                else:
                    sim_path = PROJECT_DIR / "simulator.png"
                    page_image.save(sim_path)
                    print(f"Simulator page {page_idx+1}/{len(pages)} updated: {sim_path}")
                
                if page_idx < len(pages) - 1:
                    time.sleep(4)
            
            if EPD_DRIVER_LOADED:
                epd.sleep()
            gpio_released = True
            
        else:
            # NO SPEECH TEXT -> Just draw the face without bubble once
            rotated_image = image.rotate(180)
            if EPD_DRIVER_LOADED:
                if fast_mode:
                    epd.displayPartBaseImage(epd.getbuffer(rotated_image))
                else:
                    epd.display(epd.getbuffer(rotated_image))
                epd.sleep()
                gpio_released = True
            else:
                sim_path = PROJECT_DIR / "simulator.png"
                image.save(sim_path)
                print(f"Simulator updated: {sim_path}")
            gpio_released = True
"""
    new_lines = lines[:start_idx] + [new_code] + lines[end_idx+1:]
    with open('src/ui/gotchi_ui.py', 'w') as f:
        f.writelines(new_lines)
    print("Patched successfully!")
else:
    print(f"Could not find markers. Start: {start_idx}, End: {end_idx}")

