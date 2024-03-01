from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import random, textwrap
import argparse


def generate_bingo_sheet(n, bingo_events):
    if len(bingo_events) < n**2:
        sheet_events = random.choices(bingo_events, k=n**2)
    else:
        sheet_events = random.sample(bingo_events, k=n**2)
    
    bingo_sheet = [sheet_events[i:i+n] for i in range(0, n**2, n)]
    
    return bingo_sheet


def adjust_event_image(image_path, box_size, blur_radius=0, brightness_factor=1):
    try:
        # Load and resize the event image
        event_image = Image.open(image_path).resize((box_size, box_size))
    except FileNotFoundError:
        # If specific event image is not found, create a placeholder
        event_image = Image.new('RGB', (box_size, box_size), (200, 200, 200))

    # Apply Gaussian Blur if blur_radius > 0
    if blur_radius > 0:
        event_image = event_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # Adjust brightness if brightness_factor is not 1
    if brightness_factor != 1:
        enhancer = ImageEnhance.Brightness(event_image)
        event_image = enhancer.enhance(brightness_factor)
    
    return event_image


def create_bingo_image(bingo_sheet, box_size=100, text_size=None, line_spacing=10, box_spacing=10):
    n = len(bingo_sheet)
    sheet_image_width = sheet_image_height = n * box_size + (n - 1) * box_spacing
    sheet_image = Image.new('RGB', (sheet_image_width, sheet_image_height), 'white')

    # Set the text size based on the provided parameter or default to a fraction of the box size
    if text_size is None:
        text_size = int(box_size / 2)  # Default text size
    font = ImageFont.truetype("fonts/Pacifico.ttf", size=text_size)

    for i, row in enumerate(bingo_sheet):
        for j, event in enumerate(row):
            # Load the event image
            try:
                event_image = adjust_event_image(f'event_images/f1.png', box_size, blur_radius=5, brightness_factor=1)
            except FileNotFoundError:  # If the event image is not found, create a placeholder
                event_image = Image.new('RGB', (box_size, box_size), (200, 200, 200))
            
            # If the event is in the center, use a different image
            if i == n // 2 and j == n // 2:
                event_image = adjust_event_image(f'event_images/lights.jpeg', box_size)
            else:
                draw = ImageDraw.Draw(event_image)

                wrapped_text = textwrap.wrap(event, width=10)  # Adjust the width for your needs

                # Calculate total text height (with spacing) to vertically center
                total_text_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing for line in wrapped_text]) - line_spacing
                current_height = (box_size - total_text_height) / 2

                for line in wrapped_text:
                    left, top, right, bottom = font.getbbox(line)
                    text_width = right - left
                    text_height = bottom - top
                    text_x = (box_size - text_width) / 2
                    draw.text((text_x, current_height), line, fill="white", font=font)
                    current_height += text_height + line_spacing
            
            # Paste the event image onto the sheet
            x_position = j * (box_size + box_spacing)
            y_position = i * (box_size + box_spacing)
            sheet_image.paste(event_image, (x_position, y_position))
    
    return sheet_image


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-n', "--name", help="bingo sheet name")
    argparser.add_argument('-s', "--size", help="bingo sheet size (s x s)", type=int, default=5)
    args = argparser.parse_args()

    # Load the bingo events from a text file
    with open('events.txt', 'r') as f:
        bingo_events = f.read().splitlines()
        bingo_events = [event.title() for event in bingo_events]

    # Generate the bingo sheet and create the bingo image
    bingo_sheet = generate_bingo_sheet(args.size, bingo_events)
    bingo_image = create_bingo_image(bingo_sheet, box_size=500, text_size=80, box_spacing=30)  # Specify the desired text size here

    # Save the bingo image
    bingo_image.save(f'bingo_sheets/bingo_{args.name}.png')