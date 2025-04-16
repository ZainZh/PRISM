#include <stdio.h>
#include <dlfcn.h>         
#include <unistd.h>
#include <string.h>
//#include <windows.h>
#include "../include/OpenNR-IF.h"
#define EXT_AXIS (0)

int main()
{

    sleep(1);
    char ip[222]="192.168.1.14";
    NACHI_COMMIF_INFO Info;
    memset(&Info, 0, sizeof(Info));
    Info.pcAddrs = ip;
    Info.lKind = NR_DATA_XML;
    int nXmlOpenId = NR_Open(&Info);
    if (0 < nXmlOpenId)
    {
        printf("Connect Success 1\n");
       
       
       
	   
    //记录工具编号的获/设定请求
		printf("记录工具编号的获/设定请求\n");
		int nValue18 =3;
		int nErr = NR_AcsRecordToolNo(nXmlOpenId, &nValue18, true);
		nErr = NR_AcsRecordToolNo(nXmlOpenId, &nValue18, false);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsRecordToolNo : %d\n", nValue18);
		}  
		
    //FTP有效与无???	
	NR_FTP_ENABLE value22;
	memset(&value22, 0, sizeof(value22));
	value22.nEnable = true;
	value22.csPassword = "test_password";
	int nSts = NR_AcsFtpEnable(nXmlOpenId, &value22, true);
	printf("NR_AcsFtpEnable nSts : %d\n", nSts);
	
	
	/*
	//通用输出信号的获???设定请求		
	printf("通用输出信号的获???设定请求\n");
		bool  bValue8[3];
		memset(&bValue8,0, sizeof(bValue8));
		
		bValue8[0]=true;
		bValue8[1]=true;
		bValue8[2]=true;
		nErr = NR_AcsGeneralOutputSignal(nXmlOpenId, bValue8, true, 1, 3);
		
		nErr = NR_AcsGeneralOutputSignal(nXmlOpenId, bValue8, false, 5, 3);
		printf("bValue 0: %d\n",bValue8[0]);
		printf("bValue 1: %d\n",bValue8[1]);
		printf("bValue 2: %d\n",bValue8[2]);
	
	   
    //相对位置（各轴角度移位）动作请求 
    printf("相对位置（各轴角度移位）动作请求\n");
    float fAngle[6] = {10.0f,0.0f,0.0f,0.0f,0.0f,0.0f};
		int nErr = NR_CtrlMoveJA(nXmlOpenId, fAngle, 6, 2);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_CtrlMoveJA success \n");
		}       
        
    //相对位置（工具坐标移位）动作请求
    printf("相对位置（工具坐标移位）动作请求\n");
    NR_POSE Pose = {10.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
		float fExtPos[3] ;
		memset(&fExtPos,0, sizeof(fExtPos));
		int nErr =  NR_CtrlMoveXT(nXmlOpenId, &Pose, 2, 1, 0, fExtPos, EXT_AXIS);
		if(NR_E_NORMAL == nErr)
		{
			printf(" NR_CtrlMoveXT success \n");
		}       
     
    //相对位置（机器人坐标移位）动作请求
    printf("相对位置（机器人坐标移位）动作请求\n");
    NR_POSE Pose = {10.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
		float fExtPos[3] ;
		memset(&fExtPos,0, sizeof(fExtPos));
		int nErr = NR_CtrlMoveXR(nXmlOpenId, &Pose, 2, 1, 0, fExtPos, EXT_AXIS);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_CtrlMoveXR success \n");
		} 
         
    //绝对位置（各轴角度指定）动作请求
    printf("绝对位置（各轴角度指定）动作请求\n");   
    float fAngle[6] = {-3.0f,98.0f,-5.0f,22.0f,-94.0f,-21.0f};
		int nErr = NR_CtrlMoveJ(nXmlOpenId, fAngle, 6, 2);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_CtrlMoveJ success \n");
		}
        
    
    //绝对位置（工具前端位置指定）动作请求
    printf("绝对位置（工具前端位置指定）动作请求\n");
    NR_POSE Pose = {410.0f, 21.0f, 645.0f, 22.0f, -10.0f, -154.0f};
		//float fExtPos[max(EXT_AXIS, 1)];
		float fExtPos[3] ;
		memset(&fExtPos,0, sizeof(fExtPos));
		int nErr = NR_CtrlMoveX(nXmlOpenId, &Pose, 2, 1,0,fExtPos,EXT_AXIS);
		printf("NR_CtrlMoveX  %d\n",nErr);
          
    //输入输出信号等待状态的获取
    printf("输入输出信号等待状态的获取\n");   
    bool bValue = false;
		int nErr = NR_AcsWaittingStatusSignal(nXmlOpenId, &bValue, false);
		if(NR_E_NORMAL == nErr)
		{
			printf("%s\n", (bValue? "Waitting" : "Not waitting"));
		}   
     	   
    //运转模式的获取/设定请求
    printf("运转模式的获取/设定请求\n");    
    int nValue = 1;
		int nErr = NR_AcsOperationModePlayback(nXmlOpenId, &nValue, true);
		printf("NR_AcsOperationModePlayback wirte  nErr  %d\n",nErr);
		nErr = NR_AcsOperationModePlayback(nXmlOpenId, &nValue, false);
		if(NR_E_NORMAL == nErr)
		{
				printf("Playback NO: %d\n",nValue);
		}   
      
    //STEP 进展率的获取请求
    printf("STEP 进展率的获取请求\n");
    float fValue = 0;
		int nErr = NR_AcsCheckOperationProgress(nXmlOpenId, &fValue);
		if(NR_E_NORMAL == nErr)
		{
			printf("Progress: %5.1f [%%]\n", (fValue * 100.0f));
		}
		else
		{
			printf("NR_AcsCheckSpeed reading error : %d\n", nErr);
		}   

		//检查模式的获取/设定请求
		printf("检查模式的获取/设定请求\n");
		bool bValue = false;
		int nErr = NR_AcsCheckMode(nXmlOpenId, &bValue, true);
		printf("NR_AcsCheckMode wirte  nErr  %d\n",nErr);
		NR_AcsCheckMode(nXmlOpenId, &bValue, false);
		if(NR_E_NORMAL == nErr)
		{
			printf("CheckMode: %s\n", (bValue? "Continuous" : "Non-Continuous"));
		}
	
		//检查速度的获取/设定请求
		printf("检查速度的获取/设定请求\n");
		int nValue = 5;
		int nErr = NR_AcsCheckSpeed(nXmlOpenId, &nValue, true);
		printf("NR_AcsCheckSpeed wirte  nErr  %d\n",nErr);
		nErr = NR_AcsCheckSpeed(nXmlOpenId, &nValue, false);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_AcsCheckSpeed read  %d\n",nValue);
		}	
	
		//手动速度的获取/设定请求
		printf("手动速度的获取/设定请求\n");
		int nValue = 5;
		int nErr = NR_AcsManualSpeed(nXmlOpenId, &nValue, true);
		printf("NR_AcsManualSpeed wirte  nErr  %d\n",nErr);
		nErr = NR_AcsManualSpeed(nXmlOpenId, &nValue, false);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_AcsManualSpeed read  %d\n",nValue);
		}
		
		//手动坐标系的获取/设定请求
		printf("手动坐标系的获取/设定请求\n"):
		int nValue = 1;
		int nErr = NR_AcsManualCoordinateType(nXmlOpenId, &nValue, true);
		printf("NR_AcsManualCoordinateType wirte  nErr  %d\n",nErr);
		nErr = NR_AcsManualCoordinateType(nXmlOpenId, &nValue, false);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_AcsManualCoordinateType read  %d\n",nValue);
		}
		
		//手动坐标系登录的获取请求
		printf("手动坐标系登录的获取请求\n");
		char Value23[5];
		memset(&Value23,0, sizeof(Value23));
		int nErr = NR_AcsEntryManualCoordinateType(nXmlOpenId, Value23, 200);
		if(NR_E_NORMAL == nErr)
		{
			printf("NR_AcsEntryManualCoordinateType : %s\n",Value23 );
		}

		//记录插值类型的获取/设定请求
		 printf("记录插值类型的获取/设定请求\n");
		int nValue19 =0;
		int nErr = NR_AcsInterpolationKind(nXmlOpenId, &nValue19, true);
		nErr = NR_AcsInterpolationKind(nXmlOpenId, &nValue19, false);
		if (NR_E_NORMAL == nErr)
		{
			printf("Accuracy No: %d\n", nValue19);
		}
		
		//记录加速度编号的获取/设定请求
		 printf("记录加速度编号的获取/设定请求\n");
		int nValue19 =2;
		int nErr = NR_AcsAccelerationNo(nXmlOpenId, &nValue19, true);
		nErr = NR_AcsAccelerationNo(nXmlOpenId, &nValue19, false);
		if (NR_E_NORMAL == nErr)
		{
			printf("Accuracy No: %d\n", nValue19);
		}
		
		//记录平滑度编号的获取/设定请求
		 printf("记录平滑度编号的获取/设定请求\n");
		int nValue19 =2;
		int nErr = NR_AcsRecordSmoothNo(nXmlOpenId, &nValue19, true);
		nErr = NR_AcsRecordSmoothNo(nXmlOpenId, &nValue19, false);
		if (NR_E_NORMAL == nErr)
		{
			printf("Accuracy No: %d\n", nValue19);
		}
	

		//记录精度编号的获取/设定请求
		 printf("记录精度编号的获取/设定请求\n");
		int nValue19 =4;
		int nErr = NR_AcsRecordAccuracyNo(nXmlOpenId, &nValue19, true);
		nErr = NR_AcsRecordAccuracyNo(nXmlOpenId, &nValue19, false);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsRecordAccuracyNo : %d\n", nValue19);
		}

		//记录速度的获取/设定请求
		 printf("记录速度的获取/设定请求\n");
		int nValue19 =89;
		int nErr = NR_AcsRecordSpeed(nXmlOpenId, &nValue19, true);
		nErr = NR_AcsRecordSpeed(nXmlOpenId, &nValue19, false);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsRecordSpeed : %d\n", nValue19);
		}
		
		
		
		//固定输入信号状态的获取请求
		printf("固定输入信号状态的获取请求\n");
		bool bValue23[3];
		memset(&bValue23,0, sizeof(bValue23));
		nErr = NR_AcsFixedIOInputSignal(nXmlOpenId, bValue23, 7, 3);
		if(NR_E_NORMAL == nErr)
		{
			printf("Stop : %s\n", (bValue23[0]? "ON":"OFF"));
			printf("Playback mode : %s\n", (bValue23[1]? "ON":"OFF"));
			printf("Mat switch : %s\n", (bValue23[2]? "ON":"OFF"));
		}
		
		//固定输出信号状态的获取请求
		printf("固定输出信号状态的获取请求\n");
		bool bValue24[3];
		memset(&bValue24,0, sizeof(bValue24));
		nErr = NR_AcsFixedIOOutputSignal(nXmlOpenId, bValue24, 10, 3);
		if(NR_E_NORMAL == nErr)
		{
			printf("Magnet-ON enable : %s\n", (bValue24[0]? "ON":"OFF"));
			printf("Internal/External : %s\n", (bValue24[1]? "ON":"OFF"));
			printf("WPS E-STOP ctrl : %s\n", (bValue24[2]? "ON":"OFF"));
		}
		
		//通用输入信号的获取请	
		printf("通用输入信号的获取请求\n");
		bool bValue25[10];
		memset(&bValue25,0, sizeof(bValue25));
		nErr = NR_AcsGeneralInputSignal(nXmlOpenId, bValue25, 2001, 8);
		if(NR_E_NORMAL == nErr)
		{
			for(int nCount =0; nCount < 8; nCount++)
			{
				printf("General Input Signal Monitor %d: %s\n",
				(2001 + nCount), (bValue25[nCount]? "ON":"OFF"));
			}
		}
		else
		{
			printf("NR_AcsGeneralInputSignal Input error : %d\n", nErr);
		}
		
	//输出信号名称的获	
		printf("输出信号名称的获取\n");
		int i;
		char* lpszValue[8];
		for(i=0;i<8;i++)
		{
			lpszValue[i]=(char *)malloc(sizeof(char)*255);
		}
		int nCount4 = 0;
		nErr = NR_AcsStrOutputSignalName(nXmlOpenId, lpszValue, 24, 1, 8);
		if (NR_E_NORMAL == nErr)
		{
			for (nCount4 = 0; nCount4 < 8; nCount4++)
			{
				
				printf(("%04d : %s\n"), (nCount4 + 1), lpszValue[nCount4]);
			}
		}
		else
		{
			printf("Error%d\n", nXmlOpenId);
		}

		//远程操作许可状态的获取请求
		bool bValue26 = false;
		nErr = NR_AcsRemoteMode(nXmlOpenId, &bValue26);
		if(NR_E_NORMAL == nErr)
		{
			printf("Remote Mode: %s\n", (bValue26? "ON":"OFF"));
		}


		//程序选择请求
		printf("程序选择请求\n");
		nErr = NR_CtrlProgram(nXmlOpenId, 1);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_CtrlProgram success \n");
		}
		//STEP 选择请求
		printf("STEP 选择请求\n");
		nErr = NR_CtrlStep(nXmlOpenId, 2);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_CtrlStep success \n");
		}


		//程序编号（包含堆栈）的获取请	
		printf("程序编号（包含堆栈）的获取请求\n");
		int nValue1 = 3;
		nErr = NR_AcsPrgNo(nXmlOpenId, &nValue1, 1);
		if (NR_E_NORMAL == nErr)
		{
			printf("Program No : %d\n", nValue1);
		}


		//程序编号（包含堆栈）的获取请???	
		printf("程序编号（包含堆栈）的获取请求\n");
		bool bValue = false;
		nErr = NR_AcsFixedIOStartDisplay1(nXmlOpenId, &bValue);
		if (NR_E_NORMAL == nErr)
		{
			printf("Start lamp1 : %s\n", (bValue ? "ON" : "OFF"));
		}


		//使能
		printf("使能?ON/OFF\n");
		nErr = NR_CtrlMotor(nXmlOpenId, 1);
		if (NR_E_NORMAL == nErr)
		{
			sleep(1);
			nErr = NR_CtrlMotor(nXmlOpenId, 0);
		}
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_CtrlMotor success \n");
		}



		//伺服 ON（固定输入信号）状态的获取请求		
		printf("伺服 ON（固定输入信号）状态的获取请求\n");
		bool bValue1 = false;
		nErr = NR_AcsFixedIOServoOn(nXmlOpenId, &bValue1);
		if (NR_E_NORMAL == nErr)
		{
			printf("Servo-ON : %s\n", (bValue1 ? "ON" : "OFF"));
		}


		//工具前端位置的获取请???	
		printf("工具前端位置的获取请求\n");
		float fValue[3];
		memset(&fValue, 0, sizeof(fValue));
		nErr = NR_AcsToolTipPos(nXmlOpenId, fValue, 1, 3);
		if (NR_E_NORMAL == nErr)
		{
			printf("[Position]X:%8.2f[mm]\n", fValue[0]);
			printf("[Position]Y:%8.2f[mm]\n", fValue[1]);
			printf("[Position]Z:%8.2f[mm]\n", fValue[2]);
		}


		//?各轴角度的获取请???
		printf("?各轴角度的获取请求\n");
		float fValue2[6];
		memset(&fValue2, 0, sizeof(fValue2));
		nErr = NR_AcsAxisTheta(nXmlOpenId, fValue2, 1, 6);
		if (NR_E_NORMAL == nErr)
		{
			for (int nAxis = 0; 6 > nAxis; nAxis++)
			{
				printf("Axis%d angle:%8.2f[deg??m]\n", (nAxis + 1), fValue2[nAxis]);
			}
		}
		

		//自动速度获取/设置		
		printf("自动速度获取/设置\n");
		float fValue4 = 83.0f;
		nErr = NR_AcsSpeedOverride(nXmlOpenId, &fValue4,true);
		sleep(1);
		nErr = NR_AcsSpeedOverride(nXmlOpenId, &fValue4, false);
		if (NR_E_NORMAL == nErr)
		{
				printf("NR_AcsSpeedOverride:  %.1f\n", fValue4);
		}
		else
		{
			printf("NR_AcsSpeedOverride error : %d\n", nErr);
		}


		
		//全局整数变量值的获取/设定请求		
		printf("全局整数变量值的获取/设定请求\n");
		int nValue5[3];
		memset(&nValue5, 0,sizeof(nValue5));
		nErr = NR_AcsGlobalInt(nXmlOpenId, nValue5, false, 10, 3);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsGlobalInt reading success\n");
			nErr = NR_AcsGlobalInt(nXmlOpenId, nValue5, true, 13, 3);
			if (NR_E_NORMAL == nErr)
			{
				printf("NR_AcsGlobalInt writing success\n");
			}
			else
			{
				printf("NR_AcsGlobalInt writing error : %d\n", nErr);
			}
		}
		else
		{
			printf("NR_AcsGlobalInt reading error : %d\n", nErr);
		}



		//全局实数变量值的获取/设定请求		
		printf("全局实数变量值的获取/设定请求\n");
		float fValue7[3];
		memset(&fValue7, 0,sizeof(fValue7));
		nErr = NR_AcsGlobalFloat(nXmlOpenId, fValue7, false, 10, 3);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsGlobalFloat reading success\n");
			nErr = NR_AcsGlobalFloat(nXmlOpenId, fValue7, true, 13, 3);
			if (NR_E_NORMAL == nErr)
			{
				printf("NR_AcsGlobalFloat writing success\n");
			}
			else
			{
				printf("NR_AcsGlobalFloat writing error : %d\n", nErr);
			}
		}
		else
		{
			printf("NR_AcsGlobalFloat reading error : %d\n", nErr);
		}


	//通用输出信号的获???设定请求		
	printf("通用输出信号的获???设定请求\n");
		bool  bValue8[8];
		memset(&bValue8,0, sizeof(bValue8));
		nErr = NR_AcsGeneralOutputSignal(nXmlOpenId, bValue8, false, 1, 8);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsGeneralOutputSignal reading success \n");
			nErr = NR_AcsGeneralOutputSignal(nXmlOpenId, bValue8, true, 10, 8);
			if (NR_E_NORMAL == nErr)
			{
				printf("NR_AcsGeneralOutputSignal writing success \n");
			}
			else
			{
				printf("NR_AcsGeneralOutputSignal writing error : %d\n", nErr);
			}
		}
		else
		{
			printf("NR_AcsGeneralOutputSignal reading error : %d\n", nErr);
		}


		//姿势变量值的获取/设定请求		
		printf("姿势变量值的获取/设定请求\n");
		NR_POSE_CONF Value12 = { 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f };
		nErr = NR_AcsPoseValue(nXmlOpenId, &Value12, false, 1, 1);
		if (NR_E_NORMAL == nErr)
		{
			printf("Pose1 X:%7.2f\n", Value12.fX);
			printf(" Y:%7.2f\n", Value12.fY);
			printf(" Z:%7.2f\n", Value12.fZ);
			printf(" Roll:%7.2f\n", Value12.fRoll);
			printf(" Pitch:%7.2f\n", Value12.fPitch);
			printf(" Yaw:%7.2f\n", Value12.fYaw);
			printf(" unConfig:%d\n", Value12.unConfig);
		}
		nErr = NR_AcsPoseValue(nXmlOpenId, &Value12, true, 1, 2);
		if (NR_E_NORMAL == nErr)
		{
			printf("NR_AcsPoseValue writing success \n");
		}



		//CPU 负荷的获取请???
		printf("CPU 负荷的获取请求\n");
		float fValue13 = 0.0f;
		nErr = NR_AcsCPULoad(nXmlOpenId, &fValue13);
		if (NR_E_NORMAL == nErr)
		{
			printf("CPU Load:%3.0f[%%]\n", fValue);
		}


		//系统版本的获取请???	
		printf("系统版本的获取请求\n");
		char szVersion[128];
		memset(&szVersion,0, sizeof(szVersion));
		nErr = NR_AcsVersion(nXmlOpenId, szVersion, 128);
		if (NR_E_NORMAL == nErr)
		{
			printf("System version is %s\n", szVersion);
		}
		else
		{
			printf("AcsVersion error : %d\n", nErr);
		}



		//运转准备投入（固定输出信号）状态的???	
		printf("运转准备投入（固定输出信号）状态的获\n");
		bool bValue13 = false;
		nErr = NR_AcsFixedIOMotorsOnLAMP(nXmlOpenId, &bValue13);
		if (NR_E_NORMAL == nErr)
		{
			printf("Motors-ON lamp : %s\n", (bValue13 ? "ON" : "OFF"));
		}
		else
		{
			printf("Motors-ON lamp error : %d\n", nErr);
		}
		

		//编码器获???设置		
		printf("编码器获???设置\n");
		int value14[6];
		int nSts = NR_AcsEncOffsetValue(nXmlOpenId, value14, false, 1, 6);
		printf("NR_AcsEncOffsetValue: %d\n", nSts);
		printf("1 : %d\n", value14[0]);
		printf("2 : %d\n", value14[1]);
		printf("3 : %d\n", value14[2]);
		printf("4 : %d\n", value14[3]);
		printf("5 : %d\n", value14[4]);
		printf("6 : %d\n", value14[5]);


	//输出信号名称的获???	
	printf("输出信号名称的获取\n");
		int i;
		char* lpszValue[8];
		for(i=0;i<8;i++)
		{
			lpszValue[i]=(char *)malloc(sizeof(char)*255);
		}
		int nCount4 = 0;
		nErr = NR_AcsStrOutputSignalName(nXmlOpenId, lpszValue, 24, 1, 8);
		if (NR_E_NORMAL == nErr)
		{
			char vae[255] = "fangliao放料;
			printf("放料: %s\n", vae);
			for (nCount4 = 0; nCount4 < 8; nCount4++)
			{

				printf(("%04d : %s\n"), (nCount4 + 1), lpszValue[nCount4]);
			}
		}
		else
		{
			printf("Error%d\n", nXmlOpenId);
		}


		//全局字符串变量值的获取/设定请求		
		printf("全局字符串变量值的获取/设定请求\n");
		int ii;
		char* lpszValue6[4];
		for(ii=0;ii<4;ii++)
		{
			lpszValue6[ii]=(char *)malloc(sizeof(char)*255);
		}
		nErr = NR_AcsGlobalString(nXmlOpenId, lpszValue6, 200, false, 11, 3);
		printf("NR_AcsGlobalString  read: %d\n", nErr);
		if (NR_E_NORMAL == nErr)
		{
			printf("AcsGlobalString reading success \n");
			nErr = NR_AcsGlobalString(nXmlOpenId, lpszValue6, 200, true, 14, 3);
			if (NR_E_NORMAL == nErr)
			{
				printf("AcsGlobalString writing success \n");
			}
			else
			{
				printf("AcsGlobalString writing error : %d\n", nErr);
			}
		}
		else
		{
			printf("AcsGlobalString reading error : %d\n", nErr);
		}
		



	
	//FTP设置
	NR_FTP_STATUS value;
	memset(&value, 0, sizeof(value));
	//read
	//int nSts = NR_AcsFtpStatus(nXmlOpenId, &value, false);
	//printf("NR_AcsFtpStatus read: %d\n", nSts);
	//printf("csHomeDir %S\n", value.csHomeDir);

	//wirte
	value.nConnectNum= 8;
	value.nAnonymous = 0;
	value.nTimeout = 705;
	value.csHomeDir = "D:\\WORK";
	value.nDirectoryState = 2;
	value.csLoginMessage ="nachi";
	char Password[222] ="test_password";
	value.csPassword ="test_password";
	int nSts = NR_AcsFtpStatusA(nXmlOpenId, &value, true);
	printf("NR_AcsFtpStatus wirte: %d\n", nSts);

	
	//文件删除
	char pstrRemoteFile[200] = "\\PROGRAM\\MZ07L-01-A.300";
	nSts = NR_CtrlDeleteFile(nXmlOpenId, pstrRemoteFile);
	printf("NR_CtrlDeleteFile nSts : %d\n", nSts);

	//FTP有效与无???	
	NR_FTP_ENABLE value22;
	memset(&value22, 0, sizeof(value22));
	value22.nEnable = true;
	value22.csPassword = "test_password";
	int nSts = NR_AcsFtpEnable(nXmlOpenId, &value22, true);
	printf("NR_AcsFtpEnable nSts : %d\n", nSts);

	//NR_DownLoad文件下载
	char pszIpaddress[255] = "192.168.1.105" ;
	char pstrRemoteFile[225] = "PROGRAM\\MZ07L-01-A.001" ;
	char pstrLocalFile[225] = "MZ07L-01-A.001";
	int nErr = NR_DownLoad(pszIpaddress, pstrRemoteFile, pstrLocalFile);
	if (NR_E_NORMAL == nErr)
	{
		printf("NR_DownLoad success: \n");
	}

	//NR_UpLoad文件上传
	char pszIpaddress1[255] = "192.168.1.105" ;
	char pstrRemoteFile1[225] = "PROGRAM\\MZ07L-01-A.300";
	char pstrLocalFile1[225] = "MZ07L-01-A.300";
	nErr = NR_UpLoad(pszIpaddress1, pstrRemoteFile1, pstrLocalFile1);
	if (NR_E_NORMAL == nErr)
	{
		printf("NR_UpLoad success: \n");
	}
	else
	{
		printf("NR_AcsAxisTheta error : %d\n", nErr);
	}
*/
}
	NR_Close(nXmlOpenId);
}