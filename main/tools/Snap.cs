using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Windows.Forms;

class Snap {
    [DllImport("user32.dll")]
    static extern bool SetProcessDPIAware();
    
    [DllImport("user32.dll")]
    static extern IntPtr GetDesktopWindow();
    
    [DllImport("user32.dll")]
    static extern IntPtr GetWindowDC(IntPtr hWnd);
    
    [DllImport("user32.dll")]
    static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);
    
    [DllImport("gdi32.dll")]
    static extern IntPtr CreateCompatibleDC(IntPtr hdc);
    
    [DllImport("gdi32.dll")]
    static extern IntPtr CreateCompatibleBitmap(IntPtr hdc, int nWidth, int nHeight);
    
    [DllImport("gdi32.dll")]
    static extern IntPtr SelectObject(IntPtr hdc, IntPtr hgdiobj);
    
    [DllImport("gdi32.dll")]
    static extern bool BitBlt(IntPtr hdcDest, int xDest, int yDest, int wDest, int hDest, IntPtr hdcSrc, int xSrc, int ySrc, int rop);
    
    [DllImport("gdi32.dll")]
    static extern bool DeleteDC(IntPtr hdc);
    
    [DllImport("gdi32.dll")]
    static extern bool DeleteObject(IntPtr hObject);
    
    [DllImport("gdi32.dll")]
    static extern int GetDeviceCaps(IntPtr hdc, int nIndex);
    
    const int SRCCOPY = 0x00CC0020;
    const int DESKTOPHORZRES = 118;
    const int DESKTOPVERTRES = 117;
    
    [STAThread]
    static void Main() {
        SetProcessDPIAware();
        
        IntPtr deskWnd = GetDesktopWindow();
        IntPtr deskDC = GetWindowDC(deskWnd);
        
        int capW = GetDeviceCaps(deskDC, DESKTOPHORZRES);
        int capH = GetDeviceCaps(deskDC, DESKTOPVERTRES);
        
        Console.WriteLine("Resolution: " + capW + "x" + capH);
        
        IntPtr memDC = CreateCompatibleDC(deskDC);
        IntPtr hBitmap = CreateCompatibleBitmap(deskDC, capW, capH);
        IntPtr oldBitmap = SelectObject(memDC, hBitmap);
        BitBlt(memDC, 0, 0, capW, capH, deskDC, 0, 0, SRCCOPY);
        SelectObject(memDC, oldBitmap);
        
        Bitmap bmp = Bitmap.FromHbitmap(hBitmap);
        string path = @"E:\openclaw-work\screenshot.png";
        bmp.Save(path, ImageFormat.Png);
        Console.WriteLine("Saved: " + bmp.Width + "x" + bmp.Height + " -> " + path);
        bmp.Dispose();
        
        DeleteObject(hBitmap);
        DeleteDC(memDC);
        ReleaseDC(deskWnd, deskDC);
    }
}
