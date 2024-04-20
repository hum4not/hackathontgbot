using AI.ComputerVision;
using AI.ComputerVision.DeepFake;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;


namespace FaceReplace
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string id = args[0]; //id of user to get folder
            string template = args[1]; //name of template
            string face = args[2]; //temporary file of user's face

            string searchfolder = id + "\\" + template;
            string[] filters = {"jpg", "jpeg", "png"};
            Array backgrounds = GetFilesFrom(searchfolder, filters, false);

            Bitmap Face = (Bitmap)Image.FromFile(face, true);
            Bitmap facebitmap = ImgConverter.BmpResizeM(Face, 700);

            if (!Directory.Exists(searchfolder + "\\pack"))
            {
                Directory.CreateDirectory(searchfolder + "\\pack");
            }

            var watch = System.Diagnostics.Stopwatch.StartNew();

            foreach (string background in backgrounds)
            {
                try
                {
                    Bitmap image1 = (Bitmap)Image.FromFile(background, true);
                    Bitmap image2 = ImgConverter.BmpResizeM(image1, 700);

                    Console.WriteLine("Attempting to write: " + background.Split('\\')[background.Split('\\').Length - 1]);
                    ReplFaceImg.Repl(image2, facebitmap).Save( searchfolder + $"\\pack\\" + background.Split('\\')[background.Split('\\').Length-1] );
                }
                catch (Exception ex)
                {
                    Console.WriteLine(ex.Message);
                }
            }

            watch.Stop();
            float elapsedMs = watch.ElapsedMilliseconds;
            Console.WriteLine($"\nExecution time: {elapsedMs / 1000} secs.");
        }

        public static String[] GetFilesFrom(String searchFolder, String[] filters, bool isRecursive)
        {
            List<String> filesFound = new List<String>();
            var searchOption = isRecursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
            foreach (var filter in filters)
            {
                filesFound.AddRange(Directory.GetFiles(searchFolder, String.Format("*.{0}", filter), searchOption));
            }
            return filesFound.ToArray();
        }
    }
}
