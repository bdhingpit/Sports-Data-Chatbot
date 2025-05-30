import gradio as gr
from utils.chatbot import ChatBot
from utils.ui_settings import UISettings


with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem('Text-to-Query'):
            with gr.Row() as row_one:
                chatbot = gr.Chatbot([], elem_id='chatbot', bubble_full_width=False, height=500)

                chatbot.like(UISettings.feedback, None, None)

            with gr.Row():
                input_txt = gr.Textbox(lines=4, scale=8, placeholder='Input text and press enter to submit', container=False)

            with gr.Row() as row_two:
                text_submit_btn = gr.Button(value='Submit text')
                app_functionality = gr.Dropdown(label='App functionality', choices=['Chat'], value='Chat')
                clear_btn = gr.ClearButton([input_txt, chatbot])

            txt_msg = input_txt.submit(
                fn=ChatBot.respond,
                inputs=[chatbot, input_txt, app_functionality],
                outputs=[input_txt, chatbot],
                queue=False,
            ).then(lambda: gr.Textbox(interactive=True), None, [input_txt], queue=False)

            txt_msg = text_submit_btn.click(
                fn=ChatBot.respond, inputs=[chatbot, input_txt, app_functionality], outputs=[input_txt, chatbot], queue=False
            ).then(lambda: gr.Textbox(interactive=True), None, [input_txt], queue=False)


if __name__ == '__main__':
    demo.launch()
