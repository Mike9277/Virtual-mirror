#include <opencv2/opencv.hpp>
#include <filesystem>
#include <string>
#include <fstream>
#include <json.hpp> // JSON header-only

#define OPENPOSE_FLAGS_DISABLE_POSE
#include <openpose/flags.hpp>
#include <openpose/headers.hpp>

// ---- Flags (CLI) ------------------------------------------------------------
DEFINE_string(image_path, "/opt/openpose/examples/media/COCO_val2014_000000000589.jpg",
    "Input image path.");
DEFINE_string(output_dir, "/opt/openpose/examples/media",
    "Where the rendered image will be saved.");
DEFINE_string(output_name, "",
    "Optional output filename; if empty, uses <input>_pose.png.");
DEFINE_bool(no_display, true, "Disable visual display.");
DEFINE_bool(disable_blending, true,
    "If true, render on black background (no original image).");

// ---- Helpers ----------------------------------------------------------------
static std::string deriveOutputPath(const std::string& inputPath,
    const std::string& outDir,
    const std::string& outName)
{
    namespace fs = std::filesystem;
    fs::path dir(outDir);
    if (!fs::exists(dir)) fs::create_directories(dir);

    if (!outName.empty()) return (dir / outName).string();

    fs::path in(inputPath);
    std::string stem = in.has_stem() ? in.stem().string() : "output";
    return (dir / (stem + "_pose.png")).string();
}

void saveOutput(const std::shared_ptr<std::vector<std::shared_ptr<op::Datum>>>& datumsPtr)
{
    try {
        if (datumsPtr && !datumsPtr->empty()) {
            const cv::Mat cvMat = OP_OP2CVCONSTMAT(datumsPtr->at(0)->cvOutputData);
            if (!cvMat.empty()) {
                const auto outPath = deriveOutputPath(FLAGS_image_path, FLAGS_output_dir, FLAGS_output_name);
                if (!cv::imwrite(outPath, cvMat))
                    op::opLog("Failed to write image to: " + outPath, op::Priority::High);
                else
                    op::opLog("Saved rendered pose image to: " + outPath, op::Priority::High);
            }
        }
    }
    catch (const std::exception& e) {
        op::error(e.what(), __LINE__, __FUNCTION__, __FILE__);
    }
}

void printKeypoints(const std::shared_ptr<std::vector<std::shared_ptr<op::Datum>>>& datumsPtr)
{
    try {
        if (datumsPtr && !datumsPtr->empty())
            op::opLog("Body keypoints: " + datumsPtr->at(0)->poseKeypoints.toString(), op::Priority::High);
    }
    catch (const std::exception& e) {
        op::error(e.what(), __LINE__, __FUNCTION__, __FILE__);
    }
}

// ---- Save keypoints as JSON -------------------------------------------------
void saveKeypoints(const std::shared_ptr<std::vector<std::shared_ptr<op::Datum>>>& datumsPtr)
{
    try {
        if (datumsPtr && !datumsPtr->empty())
        {
            const auto& keypointsArray = datumsPtr->at(0)->poseKeypoints;
            nlohmann::json output;
            output["version"] = 1.3;
            output["people"] = nlohmann::json::array();

            // Itera su ogni persona
            for (int person = 0; person < keypointsArray.getSize(0); person++)
            {
                std::vector<float> flatKeypoints;
                flatKeypoints.reserve(keypointsArray.getSize(1) * keypointsArray.getSize(2));

                // Appiattisci [keypoint][x,y,conf] -> [x1,y1,c1,x2,y2,c2,...]
                for (int kp = 0; kp < keypointsArray.getSize(1); kp++)
                {
                    for (int c = 0; c < keypointsArray.getSize(2); c++)
                    {
                        flatKeypoints.push_back(keypointsArray[{person, kp, c}]);
                    }
                }

                nlohmann::json personJson;
                personJson["pose_keypoints_2d"] = flatKeypoints;
                output["people"].push_back(personJson);
            }

            // Costruisci path JSON
            namespace fs = std::filesystem;
            fs::path outDir = FLAGS_output_dir;
            if (!fs::exists(outDir)) fs::create_directories(outDir);

            std::string jsonPath =
                (outDir / (fs::path(FLAGS_image_path).stem().string() + "_keypoints.json")).string();

            std::ofstream ofs(jsonPath);
            ofs << std::setw(4) << output; // pretty print
            ofs.close();

            op::opLog("Saved keypoints JSON to: " + jsonPath, op::Priority::High);
        }
        else
        {
            op::opLog("Nullptr or empty datumsPtr found.", op::Priority::High);
        }
    }
    catch (const std::exception& e)
    {
        op::error(e.what(), __LINE__, __FUNCTION__, __FILE__);
    }
}

// ---- Main -------------------------------------------------------------------
int tutorialApiCpp()
{
    try {
        op::opLog("Starting OpenPose demo...", op::Priority::High);
        const auto opTimer = op::getTimerInit();

        // 1) Wrapper
        op::Wrapper opWrapper{ op::ThreadManagerMode::Asynchronous };

        // 2) Pose config: disable_blending
        op::WrapperStructPose wsPose{};
        wsPose.renderMode = op::RenderMode::Auto;
        wsPose.blendOriginalFrame = !FLAGS_disable_blending;
        wsPose.alphaKeypoint = 1.f;
        wsPose.alphaHeatMap = 1.f;
        opWrapper.configure(wsPose);

        // optional: disable face/hand
        opWrapper.configure(op::WrapperStructFace{});
        opWrapper.configure(op::WrapperStructHand{});

        if (FLAGS_disable_multi_thread) opWrapper.disableMultiThreading();
        opWrapper.start();

        // 3) Input
        const cv::Mat cvImageToProcess = cv::imread(FLAGS_image_path);
        if (cvImageToProcess.empty()) {
            op::opLog("Could not read input image: " + FLAGS_image_path, op::Priority::High);
            return -1;
        }
        const op::Matrix imageToProcess = OP_CV2OPCONSTMAT(cvImageToProcess);

        // 4) Run
        auto datumProcessed = opWrapper.emplaceAndPop(imageToProcess);
        if (datumProcessed) {
            printKeypoints(datumProcessed);
            saveOutput(datumProcessed);    // image
            saveKeypoints(datumProcessed);  // JSON
        }
        else {
            op::opLog("Image could not be processed.", op::Priority::High);
        }

        op::printTime(opTimer, "OpenPose demo successfully finished. Total time: ",
            " seconds.", op::Priority::High);
        return 0;
    }
    catch (const std::exception&) {
        return -1;
    }
}

int main(int argc, char* argv[])
{
    gflags::ParseCommandLineFlags(&argc, &argv, true);
    return tutorialApiCpp();
}
