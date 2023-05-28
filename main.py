import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import os
import sys
text = ""

# main window

window = tk.Tk()
window["bg"] = "gray65"
window.title("Спеціальний програмний засіб приховування службових данних")
width = 400
height = 340
x = 750
y = 300
window.geometry(f'{width}x{height}+{x}+{y}')
window.resizable(False,False)

# window.iconbitmap("stegano_icon.ico")
# functions
# for Radiobuttons

global degree
degree = 1


def proverka_scolko_pomestitca_text():
    try:
        text_len = os.stat(choice_text).st_size
        label2 = tk.Label(window, text =f"Обсяг символів документу {text_len} символів", bg = "green",relief = tk.RAISED).place(x=0,y=170,width = 400, height=30)
    except:
        tk.messagebox.showwarning("Увага!","Оберіть документ")
        
        
def select_level_seria():
    global choice_seria
    choice_seria = level_seria.get()
    return choice_seria

#for buttons
def get_picture():
    global choice_picture
    choice_picture = tk.filedialog.askopenfilename()
    return choice_picture

def get_text():
    global choice_text
    choice_text = tk.filedialog.askopenfilename()
    return choice_text    

    
def proverka_scolko_pomestitca():
    try:
        start_bmp = open(choice_picture,'rb')
        global seria1
        global seria2
        global seria3
        seria1 = 0
        seria2 = 0
        seria3 = 0
        seria = 0
        while True:
            if seria == 1 or seria ==0:
                seria1 += 1
            if seria == 2:
                seria2 += 1
            if seria == 3:
                seria3 += 1
            img_byte33 = start_bmp.read(1)
            if not img_byte33:
                break
            img_proverka = int.from_bytes(img_byte33, sys.byteorder)
            bin_imgpro = format(img_proverka,'08b')
            bin_imgpro1 = bin_imgpro[:7]
            seria = 0
            for i in range(len(bin_imgpro1)-1):
                if bin_imgpro1[i] == "1" and bin_imgpro1[i+1] == "0":
                    seria += 1
            if seria ==0:
                seria +=1
        start_bmp.close()
        label2 = tk.Label(window, text =f"Можливий обсяг символів відповідно до серії: \n1 серія: {seria1//8} символів\n2 серія: {seria2//8} символів\n3 серія: {seria3//8} символів", bg = "green",relief = tk.RAISED).place(x=0,y=200,width = 400, height=170)
        return True
    except NameError:
        tk.messagebox.showwarning("Увага!","Оберіть зображення")
    except:
        tk.messagebox.showerror("Помилка","Помилка")
        
        
def encrypt():
    try:
        
        text_len = os.stat(choice_text).st_size
        print(text_len)
        if choice_seria == 1:
            if text_len >= seria1 //8:
                tk.messagebox.showwarning("Увага!","розмір тексту перевищено")
                return
        if choice_seria == 2:
            if text_len >= seria2 //8:
                tk.messagebox.showwarning("Увага!","розмір тексту перевищено")
                return
        if choice_seria == 3:
            if text_len >= seria3 //8:
                tk.messagebox.showwarning("Увага!","розмір тексту перевищено")
                return
        text = open(choice_text, 'r')
        start_bmp = open(choice_picture,'rb')
        encode_bmp = open('encoded.bmp','wb')
        
        first54 = start_bmp.read(54)
        #print(first54)
        encode_bmp.write(first54)
        
        text_mask, img_mask = create_masks(degree)
        
        print("text: {0:b}; image: {1:}".format(text_mask, img_mask))
        print(bin(0b11111111 & text_mask))
        print(bin(0b11111111 & img_mask))
        #start_bmp.seek(54, os.SEEK_CUR)
        while True:    
            symb = text.read(1)
            
            if not symb:
                break
            #print("symb {0}, bin{1:b}".format(symb, ord(symb)))
            symb = ord(symb)
            for byte_amount in range (0, 8, degree):
                count = 0
                while count == 0:
                    seria = 0
                    img_byte33 = start_bmp.read(1)
                    img_proverka = int.from_bytes(img_byte33, sys.byteorder)
                    bin_imgpro = format(img_proverka,'08b')
                    bin_imgpro1 = bin_imgpro[:7]
                    
                    for i in range(len(bin_imgpro1)-1):
                        if bin_imgpro1[i] == "1" and bin_imgpro1[i+1] == "0":
                            seria += 1
                    if seria ==0:
                        seria +=1
                    if choice_seria == seria:
                        img_byte = int.from_bytes(img_byte33, sys.byteorder) & img_mask
                        bits = symb & text_mask
                        bits >>= (8 - degree)         
                        #print("img {0}, bin {1:b}".format(img_byte, bits))        
                        img_byte |= bits
                                
                        #print('Encoded ' + str(img_byte))
                        #print('Writing ' + str(img_byte.to_bytes(1, sys.byteorder)))
                        
                        encode_bmp.write(img_byte.to_bytes(1, sys.byteorder))
                        symb <<= degree
                        count+=1
                    else:
                        encode_bmp.write(img_byte33)
        #print(start_bmp.tell())
        encode_bmp.write(start_bmp.read())
        
        text.close()
        start_bmp.close()
        encode_bmp.close()
    except NameError:
        tk.messagebox.showwarning("Увага!","Оберіть зображення, bit, seria чи текстови документ")
    except:
        tk.messagebox.showerror("Помилка","Помилка")
        
        
def decrypt():
    try:
        text = open("decoded.txt","w")
        encoded_bmp = open(choice_picture,"rb")
        
        encoded_bmp.seek(54)
           
           
        text_mask, img_mask = create_masks(degree)  
        img_mask = ~img_mask
        
        read = 0
        while True:
            symb = 0
            
            for bits_read in range(0, 8, degree):
                count = 0
                while count == 0:
                    seria = 0
                    img_byte33 = encoded_bmp.read(1)
                    img_proverka = int.from_bytes(img_byte33, sys.byteorder)
                    bin_imgpro = format(img_proverka,'08b')
                    bin_imgpro1 = bin_imgpro[:7]
                    
                    for i in range(len(bin_imgpro1)-1):
                        if bin_imgpro1[i] == "1" and bin_imgpro1[i+1] == "0":
                            seria += 1
                    if seria ==0:
                        seria +=1
                        
                    
                    if choice_seria == seria:
                        
                        img_byte = int.from_bytes(img_byte33,sys.byteorder) & img_mask
                        symb <<= degree
                        symb |= img_byte
                        count+=1
                        
                    
                        
                        
            if chr(symb) == '\n' :#and len(os.linesep) == 2
                read += 1
            elif chr(symb) == "!":
                break
                print(len(os.linesep))
            #print("symb #{0} is {1:c}".format(read, symb))
                  
            read += 1
            text.write(chr(symb))
            
        
        text.close()
        encoded_bmp.close()
    except NameError:
        tk.messagebox.showwarning("Увага!","Оберіть зображення, bit чи seria")
    except:
        tk.messagebox.showerror("Помилка","Помилка")
        
        
def create_masks(degree):
    text_mask = 0b11111111
    img_mask = 0b11111111
    
    text_mask <<= (8-degree)
    text_mask %= 256
    img_mask >>= degree
    img_mask <<= degree
    
    return text_mask,img_mask



# Widget options


level_seria = tk.IntVar()

Rbtn3=tk.Radiobutton(window, text = "1 seria",variable=level_seria,value=1,command=select_level_seria,bg = "gray65")
Rbtn4=tk.Radiobutton(window, text = "2 seria",variable=level_seria,value=2,command=select_level_seria,bg = "gray65")
Rbtn5=tk.Radiobutton(window, text = "3 seria",variable=level_seria,value=3,command=select_level_seria,bg = "gray65")


label1 = tk.Label(window, text ="Спеціальний програмний засіб\nприховування службових данних",relief = tk.RAISED,bg = "gray65") #fg = "blue", колір текту, font = ("Verdana",9) Тип і розмір тексту, justify=CENTER, вирівнювання тексту relief=SUNKEN, bd=3
label3 = tk.Label(window, text ="",relief = tk.RAISED,bg = "gray65")
    
btn1 = tk.Button(window, text='Розміри зображення',command = proverka_scolko_pomestitca,bg = "gray65")
btn6 = tk.Button(window, text='Розміри тексту',command = proverka_scolko_pomestitca_text,bg = "gray65")
btn2 = tk.Button(window, text='Закодувати',command = encrypt,bg = "gray65")
btn3 = tk.Button(window, text='Розкодувати',command = decrypt,bg = "gray65")
btn4 = tk.Button(window, text='Обрати зображення',command = get_picture,bg = "gray65")
btn5 = tk.Button(window, text='Обрати документ',command = get_text,bg = "gray65")


# Running widgets
btn4.place(x=0,y=45,width = 200, height=30)
btn5.place(x=200,y=45,width = 200, height=30)
btn6.place(x=0,y=135,width = 200, height=30)
Rbtn3.place(x=8,y=75,width = 70, height=30)
Rbtn4.place(x=110,y=75,width = 70, height=30)
Rbtn5.place(x=210,y=75,width = 70, height=30)
label1.place(x=1,y=1,width = 400, height=45)
btn1.place(x=200,y=135,width = 200, height=30)
btn2.place(x=0,y=105,width = 200, height=30)
btn3.place(x=200,y=105,width = 200, height=30)
label3.place(x=0,y=135,width = 400, height=205)

window.mainloop()


















