#include <iostream>
#include <torch/torch.h>
#include <torch/script.h>
#include <string>
#include <vector>
#include <locale>
#include <codecvt>
#include <direct.h>
#include <fstream>
typedef int64_t int64;
namespace Shirakana {

    struct WavHead {
        char RIFF[4];
        long int size0;
        char WAVE[4];
        char FMT[4];
        long int size1;
        short int fmttag;
        short int channel;
        long int samplespersec;
        long int bytepersec;
        short int blockalign;
        short int bitpersamples;
        char DATA[4];
        long int size2;
    };

    int conArr2Wav(int64 size, int16_t* input, const char* filename) {
        WavHead head = { {'R','I','F','F'},0,{'W','A','V','E'},{'f','m','t',' '},16,
                1,1,22050,22050 * 2,2,16,{'d','a','t','a'},
                0 };
        head.size0 = size * 2 + 36;
        head.size2 = size * 2;
        std::ofstream ocout;
        char* outputData = (char*)input;
        ocout.open(filename, std::ios::out | std::ios::binary);
        ocout.write((char*)&head, 44);
        ocout.write(outputData, (int32_t)(size * 2));
        ocout.close();
        return 0;
    }

    inline std::wstring to_wide_string(const std::string& input)
    {
        std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
        return converter.from_bytes(input);
    }

    inline std::string to_byte_string(const std::wstring& input)
    {
        std::wstring_convert<std::codecvt_utf8<wchar_t>> converter;
        return converter.to_bytes(input);
    }
}

#define val const auto
int main()
{
    torch::jit::Module Vits;
    std::string buffer;
    std::vector<int64> text;
    std::vector<int16_t> data;
    while(true)
    {
        while (true)
        {
            std::cin >> buffer;
            if (buffer == "end")
                return 0;
            if(buffer == "model")
            {
                std::cin >> buffer;
                Vits = torch::jit::load(buffer);
                continue;
            }
            if (buffer == "endinfer")
            {
                Shirakana::conArr2Wav(data.size(), data.data(), "temp\\tmp.wav");
                data.clear();
                std::cout << "endofinfe";
                continue;
            }
            if (buffer == "line")
            {
                std::cin >> buffer;
                while (buffer.find("endline")==std::string::npos)
                {
                    text.push_back(std::atoi(buffer.c_str()));
                    std::cin >> buffer;
                }
                val InputTensor = torch::from_blob(text.data(), { 1,static_cast<int64>(text.size()) }, torch::kInt64);
                std::array<int64, 1> TextLength{ static_cast<int64>(text.size()) };
                val InputTensor_length = torch::from_blob(TextLength.data(), { 1 }, torch::kInt64);
                std::vector<torch::IValue> inputs;
                inputs.push_back(InputTensor);
                inputs.push_back(InputTensor_length);
                if (buffer.length() > 7)
                {
                    std::array<int64, 1> speakerIndex{ (int64)atoi(buffer.substr(7).c_str()) };
                    inputs.push_back(torch::from_blob(speakerIndex.data(), { 1 }, torch::kLong));
                }
                val output = Vits.forward(inputs).toTuple()->elements()[0].toTensor().multiply(32276.0F);
                val outputSize = output.sizes().at(2);
                val floatOutput = output.data_ptr<float>();
                int16_t* outputTmp = (int16_t*)malloc(sizeof(float) * outputSize);
                if (outputTmp == nullptr) {
                    throw std::exception("内存不足");
                }
                for (int i = 0; i < outputSize; i++) {
                    *(outputTmp + i) = (int16_t) * (floatOutput + i);
                }
                data.insert(data.end(), outputTmp, outputTmp+outputSize);
                free(outputTmp);
                text.clear();
                std::cout << "endofline";
            }
        }
    }
    //model S:\VSGIT\ShirakanaTTSUI\build\x64\Release\Mods\AtriVITS\AtriVITS_LJS.pt
}