from transformers import pipeline
model = "mrm8488/codebert-base-finetuned-stackoverflow-ner"
tokenizer = "mrm8488/codebert-base-finetuned-stackoverflow-ner"
tagger = pipeline("ner",model = model, tokenizer = tokenizer,aggregation_strategy="first")

import difflib

def make_code_block(text, language="javascript"):
    """
    converts a string to a code block
    text: a string
    """
    tagg = tagger(text)
    print(tagg)
    reconsturcted_text = ""

    for entity in tagg:
        if entity["entity_group"] == "Code_Block":
            reconsturcted_text += entity["word"]

    print(reconsturcted_text)

    # remove reconstructed text from original text
    print("=================s")
    diff = difflib.ndiff(text.splitlines(keepends=True), reconsturcted_text.splitlines(keepends=True))
    # return only missing lines
    print(''.join(x[2:] for x in diff if x.startswith('- ')))







text ="""
const firstName = "Reffy";

const lastName = "Ferdiyatno";

console.log(`Hallo, nama saya ${firstName} ${lastName}.`);

  


var age = 24;

console.log(`Umur saya ${age} tahun.`);

  


const a = 1;

const b = 2;

var isMarried = a > b;

console.log(`Sataus Hubingan saya ${isMarried}.`);

  


apakah codigan di atas sesui dengan ini ?

- Variabel firstName harus bertipe data string 

- Nilai firstName tidak boleh kosong 

- Nilai lastName tidak boleh kosong 

- Variabel age harus bertipe data number 

- Variabel isMarried harus bertipe data boolean 

saya gagal terus


"""
make_code_block(text)

