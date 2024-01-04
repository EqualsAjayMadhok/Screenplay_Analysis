import requests
from bs4 import BeautifulSoup
import csv

#TODO: Features not accounted for in the initial parser that appear in other ScriptReader results
#Story Engine - HLO - Mostly summarises other sections
#Poster - HLO Executive Summary - Sometimes present. Not very necessary
#Writer's Voice - HLO Executive Summary - Changes per analysis

################################################Tool Methods##########################################################
def removeAll(array, element):
    result = []
    for i in array:
        if i != element:
            result.append(i)
    return result
def findIndex(element, array):
    index = -1
    for i in array:
        index += 1
        if i == element:
            break
    return index

########################################Classes for the separate sections###############################################
class ScriptReaderLinks:
    def __init__(self, homepage):
        self.homepage = homepage

        page = requests.get(homepage)
        soup = BeautifulSoup(page.content, "html5lib")

        self.name = soup.find("nav", attrs={"id": "navbar"}).find_next_sibling("div").h1.text

        self.ExecutiveSummary = homepage+"#exec"
        self.Overview = homepage+"#overview"
        self.Critique = homepage+"#critique"
        self.SimilarStories = homepage+"#similarto"
        self.StoryStructure = homepage+"#ss"
        self.PCR = homepage+"#pcr"
        self.ScriptWorld = homepage+"#world"
        self.StoryEngine = homepage+"#engine"

        self.Scenes = homepage+"#scene"
        self.Characters = homepage+"#characters"
        self.Script = homepage+"#cont"
        self.WriterCraft = homepage+"#craft"

        self.Correlations = homepage+"#correlations"
        self.Tropes = homepage+"#tropes"
        self.Themes = homepage+"#themes"
        self.MemorableLines = homepage+"#lines"
        self.UniqueVoice = homepage+"#voice"
        self.ProtagonistGoals = homepage+"#gpc"


class HighLevelOverview:
    def __init__(self, links):
        self.links = links
        self.ExecutiveSummary = {
            "Overview" : {},
            "PCR": {},
            "Market Analysis": {},
            "Writer's Voice": [],
            "Characters": {},
        }  # Missing "Analysis Criteria Percentiles" and "Story Shape" because they are images
        self.Overview = {
            "Overview" : "",
            "Theme": "",
            "Characters": "",
            "Conflict": "",
            "Story Telling": "",
            "Tone and Style": "",
            "Setting": "",
            "Audience": ""
        }
        self.OverviewPoints = {
        }
        self.Critique = {
            "Summary": "",
            "Story Critique": ["", ""],
            "Scene Strengths": [],
            "Scene Weaknesses": [],
            "Suggestions": []
        }
        self.CritiqueComparisons = []  # Category, Grade, Percentile, Before(script link), After(script link)
        self.SimilarStories = {}  # Story, Explanation pairs
        self.StoryStructure = ""  # Set of descriptions
        self.PCR = {
            "Screenplay Rating": "",
            "Executive Summary": "",
            "Strengths": [],
            "Areas of Improvement": [],
            "Missing Elements": [],
            "Notable Points": [],

        }
        self.ScriptWorld = {} #Tag, Description

    def parseExecutiveSummary(self):
        # TODO: Writer section, analyis criteria percentiles, story shape?

        page = requests.get(self.links.ExecutiveSummary)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#exec"}):
            section = soup.find("div", attrs={"id": "exec-overview"}).findChildren()
            previous = ""
            for child in section:
                if child.name == "p":
                    self.ExecutiveSummary["Overview"][child.contents[0].text] = " ".join(child.text.split(":")[1:]).strip()
                    previous = child.contents[0].text
                elif child.name == "ul":
                    self.ExecutiveSummary["Overview"][previous] = "\n".join(["\""+element.text.replace("\n", "").strip()+"\"" for element in child.findChildren("li")])
            counter = 0
            for key in self.ExecutiveSummary["Overview"]:
                if key == "Writing Style:":
                    self.ExecutiveSummary["Overview"][key] = [i for i in self.ExecutiveSummary["Overview"].keys()][counter+1]
                    self.ExecutiveSummary["Overview"].pop([i for i in self.ExecutiveSummary["Overview"].keys()][counter+1])
                    break
                counter += 1

            section = soup.find("div", attrs={"id": "exec-Pass/Consider/Recommend"})
            self.ExecutiveSummary["PCR"]["Recommendation"] = section.h4.text
            other = section.contents
            section = section.findAll()
            index = 0
            for child in section:
                if child.name == "strong":
                    index += 1
                    self.ExecutiveSummary["PCR"][child.text] = other[index].text.strip()
                index += 1

            section = soup.find("div", attrs={"id": "exec-Market Analaysis"}).findChildren("p")  # Typo in the website, may need to be changed someday
            previous = ""
            for child in section:
                if child.find("strong"):
                    self.ExecutiveSummary["Market Analysis"][child.contents[0].text] = child.contents[1].text.strip()
                    previous = child.contents[0].text
                else:
                    self.ExecutiveSummary["Market Analysis"][previous] = child.contents[0].text.strip()

            section = soup.find("div", attrs={"id": "exec-Writer"}).findChildren("li")
            for child in section:
                self.ExecutiveSummary["Writer's Voice"].append([i.strip() for i in child.text.split(":")])
                self.ExecutiveSummary["Writer's Voice"][-1].append(child.find("a").text.strip())

            section = soup.find("div", attrs={"id": "exec-Characters"}).findChildren("p")
            for child in section:
                self.ExecutiveSummary["Characters"][child.contents[0].text] = child.contents[1].text[1:]
    def parseOverview(self):
        page = requests.get(self.links.Overview)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#overview"}):
            self.Overview["Overview"] = soup.find("fieldset", attrs={"id": "onepager-overview"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Theme"] = soup.find("fieldset", attrs={"id": "onepager-theme"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Characters"] = soup.find("fieldset", attrs={"id": "onepager-characters"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Conflict"] = soup.find("fieldset", attrs={"id": "onepager-conflict"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Story Telling"] = soup.find("fieldset", attrs={"id": "onepager-storytelling"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Tone and Style"] = soup.find("fieldset", attrs={"id": "onepager-tone"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Setting"] = soup.find("fieldset", attrs={"id": "onepager-setting"}).contents[2].text.replace("\n", "").strip()
            self.Overview["Audience"] = soup.find("fieldset", attrs={"id": "onepager-audience"}).contents[2].text.replace("\n", "").strip()

            section = soup.find("div", attrs={"id": "onepager-percentiles"}).findChild("table").findChild("tbody")
            for row in section.findChildren("tr"):
                self.OverviewPoints[row.contents[0].text.replace("\n", "").strip()] = [row.contents[1].text.replace("\n", "").strip(), row.contents[-1].text.replace("\n", "").strip()]
    def parseCritique(self):
        # TODO: Add comparisons table reading. It currently doesn't have a clear ID
        page = requests.get(self.links.Critique)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#critique"}):
            self.Critique["Summary"] = soup.find("fieldset", attrs={"id": "overview-summary"}).contents[2].text.strip()

            self.Critique["Story Critique"][0] = soup.find("fieldset", attrs={"id": "overview-critique"}).contents[2].text.strip("\n").strip()
            self.Critique["Story Critique"][1] = soup.find("fieldset", attrs={"id": "overview-critique"}).findChildren()[2].contents[1].text

            self.Critique["Scene Strengths"] = [i.text for i in soup.find("fieldset", attrs={"id": "overview-strengths"}).findChild("ul").findChildren()]
            self.Critique["Scene Weaknesses"] = [i.text for i in soup.find("fieldset", attrs={"id": "overview-weaknesses"}).findChild("ul").findChildren()]
            self.Critique["Suggestions"] = [i.text for i in soup.find("fieldset", attrs={"id": "overview-suggestions"}).findChild("ul").findChildren()]

            section = soup.find("div", attrs={"id": "critique"})

            for row in section.find("tbody").findChildren("tr"):
                self.CritiqueComparisons.append([i.text.strip() for i in row.findChildren("td")])
    def parseSimilarStories(self):
        page = requests.get(self.links.SimilarStories)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#similarto"}):
            section = soup.find("div", attrs={"id": "similarto"}).findChild("table").findChild("tbody")
            for row in section.findChildren("tr"):
                self.SimilarStories[row.contents[0].text.strip("\n")] = row.contents[1].text.strip("\n")
    def parseStoryStructure(self):
        #NOTE: This section seems under development on the website as it has no current formatting and is just text
        page = requests.get(self.links.Critique)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#ss"}):
            section = soup.find("div", attrs={"id": "story-structure"}).findChildren("p")
            for line in section:
                self.StoryStructure += line.text+"\n"
    def parsePCR(self):
        #NOTE: Page is in beta so is subject to change
        page = requests.get(self.links.PCR)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#pcr"}):
            self.PCR["Screenplay Rating"] = soup.find("div", attrs={"id": "pcr"}).find("h4").text.strip()

            self.PCR["Executive Summary"] = soup.find("div", attrs={"id": "pcr_ES"}).p.text

            section = soup.find("div", attrs={"id": "pcr-strengths"}).ul
            for row in section:
                if row.text.strip() != "":
                    self.PCR["Strengths"].append(row.text)

            section = soup.find("div", attrs={"id": "pcr-areasOfImprovement"}).ul
            for row in section:
                if row.text.strip() != "":
                    self.PCR["Areas of Improvement"].append(row.text)

            section = soup.find("div", attrs={"id": "pcr-missingElements"}).ul
            for row in section:
                if row.text.strip() != "":
                    self.PCR["Missing Elements"].append(row.text)

            section = soup.find("div", attrs={"id": "pcr-notablePoints"}).ul
            for row in section:
                if row.text.strip() != "":
                    self.PCR["Notable Points"].append(row.text)
    def parseScriptWorld(self):
        page = requests.get(self.links.ScriptWorld)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "High Level Overview-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#world"}):
            section = soup.find("div", attrs={"id": "scriptworld"}).findChild("ul")
            for row in section.findChildren("li"):
                self.ScriptWorld[row.contents[0].text.strip("\n").strip()[:-1]] = row.contents[1].text.strip("\n")
    def parseAll(self):
        self.parseExecutiveSummary()
        self.parseOverview()
        self.parseCritique()
        self.parseSimilarStories()
        self.parseStoryStructure()
        self.parsePCR()
        self.parseScriptWorld()

    def outputExecutiveSummary(self, root):
        executiveSummaryOutput = open(root+"-ExecutiveSummary.csv", "w", newline="")
        writer = csv.writer(executiveSummaryOutput)
        writer.writerow(["Feature", "Contents"])
        for feature in self.ExecutiveSummary["Overview"]:
            writer.writerow([feature, self.ExecutiveSummary["Overview"][feature]])
        writer.writerow([])
        writer.writerow(["Feature", "Contents"])
        for feature in self.ExecutiveSummary["PCR"]:
            writer.writerow([feature, self.ExecutiveSummary["PCR"][feature]])
        writer.writerow([])
        writer.writerow(["Category", "Elaboration"])
        for feature in self.ExecutiveSummary["Market Analysis"]:
            writer.writerow([feature, self.ExecutiveSummary["Market Analysis"][feature]])
        writer.writerow([])
        writer.writerow(["Character", "Memorable Line", "Scene"])
        for feature in self.ExecutiveSummary["Writer's Voice"]:
            writer.writerow(feature)
        writer.writerow([])
        writer.writerow(["Character", "Description"])
        for feature in self.ExecutiveSummary["Characters"]:
            writer.writerow([feature, self.ExecutiveSummary["Characters"][feature]])
        writer.writerow([])
        executiveSummaryOutput.close()
    def outputOverview(self, root):
        # Currently only outputs the points
        overviewOutput = open(root + "-Overview.csv", "w", newline="")
        headers = [title for title in self.Overview]
        writer = csv.writer(overviewOutput)
        writer.writerow(headers)
        writer.writerow([self.Overview[i] for i in self.Overview])
        writer.writerow([])
        headers = ["Title", "Grade", "Percentile"]
        writer.writerow(headers)
        for row in self.OverviewPoints:
            writer.writerow([row, self.OverviewPoints[row][0], self.OverviewPoints[row][1]])
        overviewOutput.close()
    def outputCritique(self, root):
        # Not sure how to output
        critiqueOutput = open(root + "-Critique.csv", "w", newline="")
        headers = [i for i in self.Critique]
        writer = csv.writer(critiqueOutput)
        writer.writerow(headers)
        row = [
                self.Critique["Summary"],
                "\n".join(["\""+i+"\"" for i in self.Critique["Story Critique"]]),
                "\n".join(["\""+i+"\"" for i in self.Critique["Scene Strengths"]]),
                "\n".join(["\""+i+"\"" for i in self.Critique["Scene Weaknesses"]]),
                "\n".join(["\""+i+"\"" for i in self.Critique["Suggestions"]])
        ]
        writer.writerow(row)
        writer.writerow([])
        writer.writerow(["Title", "Grade", "Percentile", "Before", "After"])
        for row in self.CritiqueComparisons:
            writer.writerow(row)
        critiqueOutput.close()
    def outputSimilarStories(self, root):
        similarStoriesOutput = open(root + "-SimilarStories.csv", "w", newline="")
        headers = ["Story", "Explanation"]
        writer = csv.writer(similarStoriesOutput)
        writer.writerow(headers)
        for row in self.SimilarStories:
            writer.writerow([row, self.SimilarStories[row]])
        similarStoriesOutput.close()
    def outputStoryStructure(self, root):
        # Not sure how to output
        storyStructureOutput = open(root + "-StoryStructure.txt", "w", newline="")
        storyStructureOutput.write(self.StoryStructure)
        storyStructureOutput.close()
    def outputPCR(self, root):
        PCROutput = open(root + "-PCR.csv", "w", newline="")
        headers = ["Rating", "Executive Summary", "Strengths", "Areas of Improvement", "Missing Elements", "Notable Points"]
        writer = csv.writer(PCROutput)
        writer.writerow(headers)
        row = [self.PCR["Screenplay Rating"],
               self.PCR["Executive Summary"],
               "\n".join(["\""+i+"\"" for i in self.PCR["Strengths"]]),
               "\n".join(["\""+i+"\"" for i in self.PCR["Areas of Improvement"]]),
               "\n".join(["\""+i+"\"" for i in self.PCR["Missing Elements"]]),
               "\n".join(["\""+i+"\"" for i in self.PCR["Notable Points"]]),
               ]
        writer.writerow(row)
        PCROutput.close()
    def outputScriptWorld(self, root):
        scriptWorldOutput = open(root + "-ScriptWorld.csv", "w", newline="")
        headers = ["Category", "Description"]
        writer = csv.writer(scriptWorldOutput)
        writer.writerow(headers)
        for row in self.ScriptWorld:
            writer.writerow([row, self.ScriptWorld[row]])
        scriptWorldOutput.close()
    def outputAll(self, root):
        self.outputExecutiveSummary(root)
        self.outputOverview(root)
        self.outputCritique(root)
        self.outputSimilarStories(root)
        self.outputStoryStructure(root)
        self.outputPCR(root)
        self.outputScriptWorld(root)


class InDepthAnalysis:
    def __init__(self, links):
        self.links = links
        self.Scenes = [[]]
        self.Characters = {} #Name, Summary, Arc, Critique, Suggestions
        self.SceneAnalysis = {}
        self.WriterCraft = {"Summary": "",
                            "Key Improvement Areas": [],
                            "Suggestions": [],
                            "Additional Notes": ""
                            }

    def parseScenes(self):
        page = requests.get(self.links.Scenes)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "In Depth Analysis-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#scene"}):
            section = soup.find("div", attrs={"id": "scene"}).findChild("table")
            self.Scenes[0] = []
            for i in section.findChild("thead").findChildren("tr")[1].findChildren("th"):
                if i != "":
                    self.Scenes[0].append(i.text.replace("\n", "").strip())

            for row in section.findChild("tbody").findChildren("tr"):
                self.Scenes.append([i.text.replace("\n", "").strip() for i in row.findChildren("td")])
    def parseCharacters(self):
        page = requests.get(self.links.Characters)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "In Depth Analysis-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#characters"}):
            section = soup.find("div", attrs={"id": "characters"})
            for row in section.findChildren("fieldset"):
                self.Characters[row.legend.text] = [row.p.text, "", "", ""]

            for row in section.findChild("tbody").findChildren("tr")[1:]:
                if(row.findChildren()[0].text[1] in self.Characters):
                    self.Characters[row.findChildren()[0].text][1] = row.findChildren()[1].text
                    self.Characters[row.findChildren()[0].text][2] = row.findChildren()[2].text
                    self.Characters[row.findChildren()[0].text][3] = row.findChildren()[3].text
    def parseSceneAnalysis(self):
        page = requests.get(self.links.Scenes)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "In Depth Analysis-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#scene"}):
            counter = 1
            while soup.find("div", attrs={"id": "scenemodals"+str(counter)}):
                scene = soup.find("div", attrs={"id": "scenemodals"+str(counter)})
                sceneName = self.Scenes[counter-1][0]
                data = ["", [], [], [], [], []]  # Summary, Strengths, Weaknesses, Rating, Critique, Suggestions
                data[0] = scene.find("fieldset", attrs={"id":"scenemodal"+str(counter)+"summary"}).text.replace("\n", "").strip()
                data[1] = [i.contents[0].text.replace("\n", "").strip() for i in scene.find("fieldset", attrs={"id": "scenemodal"+str(counter)+"strengths"}).findAll("li")]
                data[2] = [i.contents[0].text.replace("\n", "").strip() for i in scene.find("fieldset", attrs={"id": "scenemodal"+str(counter)+"weaknesses"}).findAll("li")]

                ratings = scene.findAll("fieldset", class_="summary-fieldset")[1:]
                for rating in ratings:
                    for row in rating.findAll("div", class_="row"):
                        data[3].append(row.findAll("p")[0].text.split(":") + [row.findAll("p")[1].text])
                        data[3][-1][1] = data[3][-1][1].strip()

                data[4] = [i.contents[0].text.replace("\n", "").strip() for i in scene.find("fieldset", attrs={"id": "scenemodal"+str(counter)+"critique"}).findAll("li")]
                data[5] = [i.contents[0].text.replace("\n", "").strip() for i in scene.find("fieldset", attrs={"id": "scenemodal"+str(counter)+"suggestions"}).findAll("li")]
                counter += 1

                self.SceneAnalysis[sceneName] = data

    def parseWriterCraft(self):
        page = requests.get(self.links.WriterCraft)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "In Depth Analysis-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#craft"}):
            self.WriterCraft["Summary"] = soup.find("p", attrs={"id": "craft-overall"}).text

            section = soup.find("div", attrs={"id": "craft"})
            flag1 = False
            for i in section.findChildren("div"):
                if i.find("h3"):
                    if i.h3.text.strip() == "Key Improvement Areas" and not flag1:
                        flag1 = True
                        for j in i.findChildren("div", attrs={"class": "card mt-3"}):
                            self.WriterCraft["Key Improvement Areas"].append([j.contents[1].text.replace("\n", "").strip(), j.contents[3].text.replace("\n", "").strip()])
                    if i.h3.text.strip() == "Suggestions":
                        for j in i.find("tbody").findChildren("tr"):
                            self.WriterCraft["Suggestions"].append([j.contents[1].text, j.contents[3].text, j.contents[5].text])
                if i.find("strong"):
                    if i.strong.text.strip() == "Additional Notes:":
                        self.WriterCraft["Additional Notes"] = i.contents[2].text.strip()
    def parseAll(self):
        self.parseScenes()
        self.parseCharacters()
        self.parseSceneAnalysis()
        self.parseWriterCraft()

    def outputScenes(self, root):
        scenesOutput = open(root + "-Scenes.csv", "w", newline="")
        writer = csv.writer(scenesOutput)
        for row in self.Scenes:
            writer.writerow(row)
        scenesOutput.close()
    def outputCharacters(self, root):
        charactersOutput = open(root + "-Characters.csv", "w", newline="")
        headers = ["Name", "Summary", "Arc", "Critique", "Suggestions"]
        writer = csv.writer(charactersOutput)
        writer.writerow(headers)
        for character in self.Characters:
            writer.writerow([character]+self.Characters[character])
        charactersOutput.close()
    def outputSceneAnalysis(self, root):
        sceneAnalysisOutput = open(root + "-SceneAnalysis.csv", "w", newline="")
        headers = ["Scene Name", "Summary", "Strengths", "Weaknesses"]+[rating[0] for rating in self.SceneAnalysis[list(self.SceneAnalysis.keys())[0]][3]]+["Critique", "Suggestions"]
        writer = csv.writer(sceneAnalysisOutput)
        writer.writerow(headers)
        for scene in self.SceneAnalysis:
            row = [
                scene,
                self.SceneAnalysis[scene][0],
                "\n".join(["\""+i+"\"" for i in self.SceneAnalysis[scene][1]]),
                "\n".join(["\""+i+"\"" for i in self.SceneAnalysis[scene][2]])
            ]
            for rating in self.SceneAnalysis[scene][3]:
                row.append(rating[1])  # Currently just the number, no room for the text but can be added
            row.append("\n".join(["\""+i+"\"" for i in self.SceneAnalysis[scene][4]]))
            row.append("\n".join(["\""+i+"\"" for i in self.SceneAnalysis[scene][5]]))
            writer.writerow(row)
        sceneAnalysisOutput.close()
    def outputWriterCraft(self, root):
        writerCraftOutput = open(root + "-WriterCraft.csv", "w", newline="")
        writer = csv.writer(writerCraftOutput)
        writer.writerow(["Summary"])
        writer.writerow([self.WriterCraft["Summary"]])
        writer.writerow([])
        writer.writerow(["Key Improvement Area", "Elaboration"])
        for row in self.WriterCraft["Key Improvement Areas"]:
            writer.writerow(row)
        writer.writerow([])
        writer.writerow(["Suggestion Type", "Suggestion", "Rationale"])
        for row in self.WriterCraft["Suggestions"]:
            writer.writerow(row)
        writerCraftOutput.close()
    def outputAll(self, root):
        self.outputScenes(root)
        self.outputCharacters(root)
        self.outputSceneAnalysis(root)
        self.outputWriterCraft(root)


class ContextualInsights:
    def __init__(self, links):
        self.links = links
        self.Correlations = []  # Pattern, Explanation
        self.Tropes = []  # Trope, Trope Details, Trope Explanation
        self.UniqueVoice = []  #Idea, Elaboration
        self.Themes = []  # Theme, Theme Details, Theme Explanation
        self.MemorableLines = []  # Scene, Line
        self.ProtagonistGoals = {}

    def parseCorrelations(self):
        page = requests.get(self.links.Correlations)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "Contextual Insights-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#correlations"}):
            section = soup.find("div", attrs={"id": "correlations"})
            for row in section.find("tbody").findChildren("tr"):
                self.Correlations.append([row.contents[0].text, row.contents[1].text])
    def parseTropes(self):
        page = requests.get(self.links.Tropes)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "Contextual Insights-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#tropes"}):
            section = soup.find("div", attrs={"id": "tropes"})
            for row in section.find("tbody").findChildren("tr"):
                self.Tropes.append([row.contents[0].text, row.contents[1].text, row.contents[2].text])
    def parseThemes(self):
        #NOTE: Currently ignoring resources section at the bottom of the page until told otherwise
        page = requests.get(self.links.Themes)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "Contextual Insights-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#themes"}):
            section = soup.find("div", attrs={"id": "themes"})
            for row in section.find("tbody").findChildren("tr"):
                try:
                    self.Themes.append([row.contents[0].text, row.contents[1].text, row.contents[2].text])
                except:
                    pass
    def parseMemorableLines(self):
        page = requests.get(self.links.MemorableLines)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "Contextual Insights-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#lines"}):
            section = soup.find("div", attrs={"id": "lines"})
            for row in section.find("tbody").findChildren("tr"):
                self.MemorableLines.append([row.contents[0].text, row.contents[1].text])
    def parseUniqueVoice(self):
        page = requests.get(self.links.UniqueVoice)
        soup = BeautifulSoup(page.content, "html5lib")
        if soup.find("button", attrs={"id": "Contextual Insights-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#voice"}):
            section = soup.find("div", attrs={"id": "voice"})
            if section.find("thead"):
                for row in section.find("thead").findChildren("tr")[1:]:
                    self.UniqueVoice.append([row.contents[1].text.replace("\n", ""), row.contents[3].text])
    def parseProtagonistGoals(self):
        page = requests.get(self.links.ProtagonistGoals)
        soup = BeautifulSoup(page.content, "html5lib")

        if soup.find("button", attrs={"id": "Contextual Insights-tab"}).find_next_sibling("ul").find("a", attrs={"href": "#gpc"}):
            section = soup.find("div", attrs={"id": "gpc"})
            for row in section.find("tbody").findChildren("tr"):
                self.ProtagonistGoals[removeAll(row.contents, "\n")[0].text.replace("\n", "")] = removeAll(row.contents, "\n")[1].text.replace("\n", "")

            section = section.findChild("div")
            for element in section.findChildren():
                if element.name == "b":
                    self.ProtagonistGoals[element.text[:-1]] = section.contents[findIndex(element.text, [i.text for i in section.contents])+1].text.replace("\n", "").strip()
    def parseAll(self):
        self.parseCorrelations()
        self.parseTropes()
        self.parseUniqueVoice()
        self.parseThemes()
        self.parseMemorableLines()
        self.parseProtagonistGoals()

    def outputCorrelations(self, root):
        correlationsOutput = open(root + "-Correlations.csv", "w", newline="")
        headers = ["Pattern", "Explanation"]
        writer = csv.writer(correlationsOutput)
        writer.writerow(headers)
        for row in self.Correlations:
            writer.writerow(row)
        correlationsOutput.close()
    def outputTropes(self, root):
        tropesOutput = open(root + "-Tropes.csv", "w", newline="")
        headers = ["Trope", "Trope Details", "Trope Explanation"]
        writer = csv.writer(tropesOutput)
        writer.writerow(headers)
        for row in self.Tropes:
            writer.writerow(row)
        tropesOutput.close()
    def outputThemes(self, root):
        themesOutput = open(root + "-Themes.csv", "w", newline="")
        headers = ["Theme", "Theme Details", "Theme Explanation"]
        writer = csv.writer(themesOutput)
        writer.writerow(headers)
        for row in self.Themes:
            writer.writerow(row)
        themesOutput.close()
    def outputMemorableLines(self, root):
        memorableLinesOutput = open(root + "-MemorableLines.csv", "w", newline="")
        headers = ["Scene Number", "Line"]
        writer = csv.writer(memorableLinesOutput)
        writer.writerow(headers)
        for row in self.MemorableLines:
            writer.writerow(row)
        memorableLinesOutput.close()
    def outputUniqueVoice(self, root):
        uniqueVoiceOutput = open(root + "-UniqueVoice.csv", "w", newline="")
        headers = ["Idea", "Elaboration"]
        writer = csv.writer(uniqueVoiceOutput)
        writer.writerow(headers)
        for row in self.UniqueVoice:
            writer.writerow(row)
        uniqueVoiceOutput.close()
    def outputProtagonistGoals(self, root):
        protagonistGoalsOutput = open(root + "-ProtagonistGoals.csv", "w", newline="")
        headers = ["Category", "Elaboration"]
        writer = csv.writer(protagonistGoalsOutput)
        writer.writerow(headers)
        for row in self.ProtagonistGoals:
            writer.writerow([row, self.ProtagonistGoals[row]])
        protagonistGoalsOutput.close()
    def outputAll(self, root):
        self.outputCorrelations(root)
        self.outputTropes(root)
        self.outputThemes(root)
        self.outputMemorableLines(root)
        self.outputUniqueVoice(root)
        self.outputProtagonistGoals(root)


#Test URLs
URLS = {
    "FBTB": "https://scriptreader.ai/disp.php?movieid=36ab771eba23f49d7ae43af88c601f3de8fccb201250906a4085444ae765f2db",
    "RUMI": "https://scriptreader.ai/disp.php?movieid=2a3d253e5273a3e67096224cca77d84c7fc096b0515320989df59d4b177636fe",
    "JAC": "https://scriptreader.ai/disp.php?movieid=68ac846d8dc1c75da907a425479be9ddf766b4dc1e172b195cfbb9738ed895dc",
    "Flyers": "https://scriptreader.ai/disp.php?movieid=bc10b57514d76124b4120a34db2224067fed660b09408ade0b14b582946ff2fc",
    "CAMP": "https://scriptreader.ai/disp.php?movieid=b192c9bbefcbd7b0c7bf0d22de062086cc167f80d5287c2351a5748ad3a085fd",
    "ISOCZ": "https://scriptreader.ai/disp.php?movieid=d2d8f9273e06e9e9c574d1681d0c664bb92716dc71883c051256b2cda975e757",
    "Starlore": "https://scriptreader.ai/disp.php?movieid=fb87e6cf60af08595bd9fcf1f006a12f1338cb4480acea383b3b65da10bb9f28",
    "Faith and Fury": "https://scriptreader.ai/disp.php?movieid=7ca2552ffd0e38deee9b22af6d3e8ce9fe88ec88162469b02602ff64cc41d2a6"
}
def testSpecific(link):
    allLinks = ScriptReaderLinks(URLS[link])
    fileName = link
    print("Running on " + link)
    hlo = HighLevelOverview(allLinks)
    hlo.parseAll()
    hlo.outputAll(fileName)

    ida = InDepthAnalysis(allLinks)
    ida.parseAll()
    ida.outputAll(fileName)

    ci = ContextualInsights(allLinks)
    ci.parseAll()
    ci.outputAll(fileName)
def testAll():
    for link in URLS:
        try:
            allLinks = ScriptReaderLinks(URLS[link])
            fileName = link
            print("Running on "+link)
            hlo = HighLevelOverview(allLinks)
            hlo.parseAll()
            hlo.outputAll(fileName)

            ida = InDepthAnalysis(allLinks)
            ida.parseAll()
            ida.outputAll(fileName)

            ci = ContextualInsights(allLinks)
            ci.parseAll()
            ci.outputAll(fileName)
        except Exception as e:
            print("Error on "+link+": "+str(e))

testAll()

'''while(True):
    try:
        URL = input("Input the URL of the ScriptReader.ai analysis: ")
        print("Validating URL...")
        allLinks = ScriptReaderLinks(URL)
        print("URL Validated!")
        fileName = allLinks.name
        break
    except:
        print("Invalid URL")

print("Setting Up...")
print("Running...")

hlo = HighLevelOverview(allLinks)
hlo.parseAll()
hlo.outputAll(fileName)

ida = InDepthAnalysis(allLinks)
ida.parseAll()
ida.outputAll(fileName)

ci = ContextualInsights(allLinks)
ci.parseAll()
ci.outputAll(fileName)

print("Finished!")'''
