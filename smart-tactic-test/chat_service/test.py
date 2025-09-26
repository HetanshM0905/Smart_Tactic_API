import google.generativeai as genai
genai.configure(api_key="AIzaSyDTpDeQpy6Ql6s1Ug6HsZId5jACVPNwJJI")
print(genai.list_models())
for i in genai.list_models():
    print(i)