using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.Script.Serialization;
using System.Windows.Forms;

namespace Party4 {
    sealed class Mini {
        public int Id; public string Name;
        public Mini(int id, string name) { Id=id; Name=name; }
        public override string ToString() { return Name; }
    }
    sealed class Launcher : Form {
        readonly Color navy=Color.FromArgb(18,25,45), panel=Color.FromArgb(28,39,64), gold=Color.FromArgb(255,209,91);
        readonly string root=AppDomain.CurrentDomain.BaseDirectory;
        readonly TextBox disc=new TextBox();
        readonly ComboBox[] characters=new ComboBox[4], roles=new ComboBox[4];
        readonly ComboBox resolution=new ComboBox(), difficulty=new ComboBox(), mini=new ComboBox();
        readonly NumericUpDown turns=new NumericUpDown();
        readonly CheckBox wide=new CheckBox(), fullscreen=new CheckBox(), bonus=new CheckBox();
        readonly TrackBar volume=new TrackBar();
        readonly Label status=new Label();
        readonly List<Button> launchButtons=new List<Button>();
        bool changing; Process game;
        public Launcher() {
            Text="Party 4 • Native preview"; ClientSize=new Size(920,760); MinimumSize=MaximumSize=Size;
            FormBorderStyle=FormBorderStyle.FixedSingle; MaximizeBox=false; StartPosition=FormStartPosition.CenterScreen;
            BackColor=navy; ForeColor=Color.White; Font=new Font("Segoe UI",10);
            Label title=LabelAt("PARTY 4",30,23,500,46,28,FontStyle.Bold); title.ForeColor=gold;
            LabelAt("NATIVE PC PREVIEW",33,73,650,25,10,FontStyle.Bold).ForeColor=Color.LightSteelBlue;
            LabelAt("Toad’s Midway Madness",30,121,840,42,23,FontStyle.Bold);
            LabelAt("One board. Four familiar faces. Nine minigames.",32,165,820,26,11,FontStyle.Regular);
            LabelAt("YOUR GAME IMAGE",32,210,400,22,9,FontStyle.Bold).ForeColor=Color.LightSteelBlue;
            disc.SetBounds(32,236,742,29); disc.BackColor=panel; disc.ForeColor=Color.White; disc.BorderStyle=BorderStyle.FixedSingle; Controls.Add(disc);
            Button browse=ButtonAt("Browse",788,233,100,33); browse.Click+=(s,e)=>{using(var picker=new OpenFileDialog { Filter="GameCube game image|*.rvz;*.iso;*.gcm|All files|*.*" }) if(picker.ShowDialog(this)==DialogResult.OK) disc.Text=picker.FileName;};
            string savedPath=Path.Combine(root,"profile","disc-path.txt");
            disc.Text=File.Exists(savedPath)?File.ReadAllText(savedPath):"C:\\Users\\avery\\Documents\\Mario Party 4 (Europe) (En,Fr,De,Es,It) (Rev 2).rvz";
            string[] names={"Mario","Luigi","Peach","Yoshi"};
            for(int i=0;i<4;i++) {
                int seat=i, x=32+i*217;
                LabelAt("PLAYER "+(i+1),x,291,195,22,9,FontStyle.Bold).ForeColor=gold;
                characters[i]=ComboAt(x,320,194,names); characters[i].SelectedIndex=i;
                roles[i]=ComboAt(x,358,194,new[]{"Local player","CPU"}); roles[i].SelectedIndex=i==0?0:1;
                characters[i].SelectedIndexChanged+=(s,e)=>{
                    if(changing)return; changing=true;
                    int chosen=characters[seat].SelectedIndex;
                    var duplicate=Enumerable.Range(0,4).FirstOrDefault(j=>j!=seat&&characters[j]!=null&&characters[j].SelectedIndex==chosen);
                    bool hasDuplicate=Enumerable.Range(0,4).Any(j=>j!=seat&&characters[j]!=null&&characters[j].SelectedIndex==chosen);
                    if(hasDuplicate){int unused=Enumerable.Range(0,4).First(n=>!characters.Where(c=>c!=null).Any(c=>c.SelectedIndex==n));characters[duplicate].SelectedIndex=unused;}
                    changing=false;
                };
            }
            LabelAt("PARTY SETTINGS",32,416,260,22,9,FontStyle.Bold).ForeColor=Color.LightSteelBlue;
            LabelAt("Turns",32,450,65,26,10,FontStyle.Regular); turns.SetBounds(94,447,77,30); turns.Minimum=5;turns.Maximum=50;turns.Increment=5;turns.Value=10;Controls.Add(turns);
            LabelAt("CPU",194,450,50,26,10,FontStyle.Regular); difficulty=ComboAt(244,447,127,new[]{"Easy","Normal","Hard","Expert"}); difficulty.SelectedIndex=1;
            bonus.Text="Bonus stars";bonus.Checked=true;bonus.SetBounds(32,489,160,25);Controls.Add(bonus);
            LabelAt("DISPLAY & SOUND",414,416,450,22,9,FontStyle.Bold).ForeColor=Color.LightSteelBlue;
            resolution=ComboAt(414,447,150,new[]{"Auto resolution","1× resolution","2× resolution","3× resolution","4× resolution"}); resolution.SelectedIndex=3;
            wide.Text="16:9 widescreen";wide.Checked=true;wide.SetBounds(586,446,192,29);Controls.Add(wide);
            fullscreen.Text="Fullscreen";fullscreen.SetBounds(779,446,112,29);Controls.Add(fullscreen);
            LabelAt("Volume",414,489,75,26,10,FontStyle.Regular);volume.SetBounds(488,480,185,45);volume.Minimum=0;volume.Maximum=100;volume.Value=70;volume.TickStyle=TickStyle.None;Controls.Add(volume);
            Button party=ButtonAt("START PARTY",32,548,338,51);party.BackColor=gold;party.ForeColor=navy;party.Font=new Font(Font,FontStyle.Bold);party.Click+=(s,e)=>Launch(0);launchButtons.Add(party);
            mini=ComboAt(414,548,330,new object[]{
                new Mini(403,"FFA · Booksquirm"),new Mini(407,"FFA · Domination"),new Mini(409,"FFA · Toad’s Quick Draw"),
                new Mini(416,"1 vs 3 · Candlelight Flight"),new Mini(418,"1 vs 3 · Hide and Go BOOM!"),new Mini(423,"1 vs 3 · GOAL!!!"),
                new Mini(425,"2 vs 2 · The Great Deflate"),new Mini(430,"2 vs 2 · Pair-a-Sailing"),new Mini(432,"2 vs 2 · Dungeon Duos")});mini.SelectedIndex=0;
            Button practice=ButtonAt("Practice",759,546,129,36);practice.Click+=(s,e)=>Launch(((Mini)mini.SelectedItem).Id);launchButtons.Add(practice);
            LabelAt("KEYBOARD  WASD move · J A · K B · L X · I Y · Enter Start · Q Z",32,626,856,25,10,FontStyle.Regular).ForeColor=Color.LightSteelBlue;
            LabelAt("Gamepads: connect before launch. Press Esc in-game for controller and video settings.",32,655,856,24,9,FontStyle.Regular).ForeColor=Color.LightSteelBlue;
            status.SetBounds(32,707,856,38);status.ForeColor=gold;status.Text="Offline preview • Online rooms are still being implemented.";Controls.Add(status);
            FormClosing+=(s,e)=>{if(game!=null&&!game.HasExited){e.Cancel=true;status.Text="Close the game window first, then close this launcher.";}};
        }
        Label LabelAt(string text,int x,int y,int w,int h,float size,FontStyle style){var l=new Label{Text=text,Font=new Font("Segoe UI",size,style),AutoSize=false};l.SetBounds(x,y,w,h);Controls.Add(l);return l;}
        Button ButtonAt(string text,int x,int y,int w,int h){var b=new Button{Text=text,FlatStyle=FlatStyle.Flat,BackColor=panel,ForeColor=Color.White,Cursor=Cursors.Hand};b.FlatAppearance.BorderColor=Color.FromArgb(66,83,111);b.SetBounds(x,y,w,h);Controls.Add(b);return b;}
        ComboBox ComboAt(int x,int y,int width,object[] items){var c=new ComboBox{DropDownStyle=ComboBoxStyle.DropDownList,BackColor=panel,ForeColor=Color.White,FlatStyle=FlatStyle.Flat};c.SetBounds(x,y,width,31);c.Items.AddRange(items);Controls.Add(c);return c;}
        void Launch(int miniId) {
            try {
                string image=Path.GetFullPath(disc.Text.Trim().Trim('"'));
                if(!File.Exists(image))throw new IOException("Choose your Mario Party 4 game image first.");
                string engine=Path.Combine(root,"engine"),exe=Path.Combine(engine,"partyboard.exe"),profile=Path.Combine(root,"profile");
                if(!File.Exists(exe))throw new IOException("The native engine is still being packaged. Please wait for the build to finish.");
                Directory.CreateDirectory(profile);
                var json=new JavaScriptSerializer();var settings=new Dictionary<string,object>();string cfg=Path.Combine(profile,"config.json");
                if(File.Exists(cfg)){try{settings=json.Deserialize<Dictionary<string,object>>(File.ReadAllText(cfg));}catch{}}
                settings["backend.isoPath"]=image;settings["backend.skipPreLaunchUI"]=true;settings["backend.wasPresetChosen"]=true;
                settings["backend.checkForUpdates"]=false;settings["backend.enableCrashReporting"]=false;
                settings["game.internalResolutionScale"]=resolution.SelectedIndex;settings["game.shadowResolutionMultiplier"]=2;
                settings["video.targetFrameRate"]=60;settings["video.enableAdaptiveWidescreen"]=wide.Checked;settings["video.lockAspectRatio"]=!wide.Checked;
                settings["video.enableFullscreen"]=fullscreen.Checked;settings["audio.masterVolume"]=volume.Value;
                File.WriteAllText(cfg,json.Serialize(settings),new UTF8Encoding(false));File.WriteAllText(Path.Combine(profile,"disc-path.txt"),image);
                int humans=0;string roster="";for(int i=0;i<4;i++){if(roles[i].SelectedIndex==0)humans|=1<<i;roster+=characters[i].SelectedIndex;}
                string logs=Path.Combine(root,"logs",DateTime.Now.ToString("yyyyMMdd-HHmmss")+"-"+Guid.NewGuid().ToString("N").Substring(0,6));Directory.CreateDirectory(logs);
                var start=new ProcessStartInfo(exe){WorkingDirectory=engine,UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true};
                start.EnvironmentVariables["PARTYBOARD_TEST_PROFILE"]=profile;start.EnvironmentVariables["PARTYBOARD_CRASH_DIR"]=logs;
                start.EnvironmentVariables["PARTYBOARD_DISC_IMAGE"]=image;start.EnvironmentVariables["PARTY4_SESSION"]="1";
                start.EnvironmentVariables["PARTY4_HUMANS"]=humans.ToString();start.EnvironmentVariables["PARTY4_ROSTER"]=roster;
                start.EnvironmentVariables["PARTY4_TURNS"]=turns.Value.ToString();start.EnvironmentVariables["PARTY4_DIFFICULTY"]=difficulty.SelectedIndex.ToString();
                start.EnvironmentVariables["PARTY4_BONUS"]=bonus.Checked?"1":"0";start.EnvironmentVariables["PARTY4_MINIGAME"]=miniId.ToString();
                start.EnvironmentVariables.Remove("PARTY4_TEST_MULTIPLE");start.EnvironmentVariables.Remove("PARTYBOARD_AUDIO_DUMP");
                var watch=Stopwatch.StartNew(); var stdout=new StreamWriter(Path.Combine(logs,"game.log")){AutoFlush=true};var stderr=new StreamWriter(Path.Combine(logs,"error.log")){AutoFlush=true};
                game=new Process{StartInfo=start,EnableRaisingEvents=true};
                game.OutputDataReceived+=(s,e)=>{if(e.Data!=null)lock(stdout)stdout.WriteLine(e.Data);};game.ErrorDataReceived+=(s,e)=>{if(e.Data!=null)lock(stderr)stderr.WriteLine(e.Data);};
                game.Exited+=(s,e)=>{game.WaitForExit();stdout.Dispose();stderr.Dispose();if(!IsDisposed)BeginInvoke((Action)(()=>{foreach(var b in launchButtons)b.Enabled=true;status.Text=watch.Elapsed.TotalSeconds<3?"The game could not start. Close any older Party Board window and try again.":game.ExitCode==0?"Session finished. Ready for another party.":"The game stopped unexpectedly. Details were saved in the logs folder.";}));};
                foreach(var b in launchButtons)b.Enabled=false;status.Text="Playing • Close the game window to return here.";
                if(!game.Start())throw new IOException("Could not launch the native game.");game.BeginOutputReadLine();game.BeginErrorReadLine();
            }catch(Exception ex){foreach(var b in launchButtons)b.Enabled=true;status.Text=ex.Message;}
        }
        [STAThread] static void Main(){Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);Application.Run(new Launcher());}
    }
}
