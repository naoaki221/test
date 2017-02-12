//
// coding: cp932
// vim: set tabstop=8 expandtab shiftwidth=4 softtabstop=4:
// vim: set foldmethod=marker:

using System;
using System.IO;
using System.Data;
using System.Text;
using System.Linq;
using System.Reflection;
using System.util.collections;

using System.Windows.Forms;

using iTextSharp.text;
using iTextSharp.text.pdf;
using iTextSharp.text.pdf.parser;

public class Hello3
{
    public static void Main(string[] args)
    {
        string outFile = "";
        string[] files = new string[args.Length];
        args.CopyTo(files, 0);
        Array.Sort(files, StringComparer.InvariantCulture);

        MemoryStream merged_dest; 
        
        MemoryStream dest = new MemoryStream();
        Document doc = new Document();
        PdfCopy copy = new PdfCopy(doc, dest);
        doc.Open();
        for (int i = 0; i < files.Length; i ++) {
            //Console.Write(files[i] + "\r\n");
            //Console.Write(System.IO.Path.GetFileNameWithoutExtension(files[i]) + "\r\n");
            if (i == 0) {
                outFile = System.IO.Path.GetFileNameWithoutExtension(files[i]) + "_out1.pdf";
            }
            PdfReader reader = new PdfReader(files[i]);
            copy.AddDocument(reader);
            reader.Close();
        }
        doc.Close();
        merged_dest = new MemoryStream(dest.ToArray());

        merged_dest.Seek(0, SeekOrigin.Begin);

        PdfReader PDFReader = new PdfReader(merged_dest);
        FileStream newStream = new FileStream(outFile, FileMode.Create, FileAccess.Write);
        PdfStamper PDFStamper = new PdfStamper(PDFReader, newStream);

        for (int iCount = 0; iCount < PDFStamper.Reader.NumberOfPages; iCount ++) {
            Rectangle size= PDFReader.GetPageSize(iCount + 1); 
            float ratio = (size.Width + size.Height) / (612f + 792f);
            PdfContentByte PDFData = PDFStamper.GetOverContent(iCount + 1);
            BaseFont baseFont = BaseFont.CreateFont(BaseFont.HELVETICA, BaseFont.WINANSI, BaseFont.EMBEDDED);
            PDFData.BeginText();
            PDFData.SetFontAndSize(baseFont, 20 * ratio);
            float fx, fy;
            if (size.Width < size.Height) {
                fx = 500f; fy = 20f;
            } else {
                fx = 550f; fy = 20f;
            }
            PDFData.ShowTextAligned(PdfContentByte.ALIGN_CENTER, 
                String.Format("{0}/{1}", iCount + 1, PDFStamper.Reader.NumberOfPages), fx, fy, 0);
            PDFData.EndText();
        }
        
        PDFStamper.Close();
        PDFReader.Close();
    }
}


