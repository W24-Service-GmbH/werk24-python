# Werk24 Client

- Understand the content of your PDF- and image-based Technical Drawings with a simple API call.

Werk24 offers an easy to use API to extract information from PDF- and image-based Technical Drawings.
With the API are able to obtain:

- Thumbnails of the Page / Canvas / Sectionals (Cuts and Perspectives)
- Measures incl. tolerances

Check our website at [https://www.werk24.biz](https://www.werk24.biz).
The project is persistently improved. Get in touch with us to obtain your API key.

## Installation

Pip installation

    pip install werk24

## Documentation

See [https://werk24.github.io/docs/](https://werk24.github.io/docs/).

## CLI

To get a first impression, you can run the CLI:

    usage: w24cli techread [-h] [--ask-techread-started] [--ask-page-thumbnail]
                       [--ask-sheet-thumbnail] [--ask-sectional-thumbnail]
                       [--ask-variant-measures]
                       input_files

## Example

    import sys
    import asyncio
    from werk24 import W24TechreadClient, W24AskVariantOverallDimensions, Hook

    # get the drawing
    with open(drawing_path, "rb") as drawing_handle
        drawing_bytes = drawing_handle.read()

    async def main(drawing_path:str) -> None:

        # define the hooks
        hooks = [Hook(ask=W24AskVariantOverallDimensions(),function=print)]

        # make the session and start the reading process
        client = W24TechreadClient.make_from_env()
        async with client as session
            session.read_drawing_with_hooks(drawing_bytes, hooks)

    if  __name__ == "__main__":
        try:
            drawing_path = sys.argv[1]

        except KeyError:
            sys.exit("Drawing Path Required as first argument")

        asyncio.run(main(drawing_path))
