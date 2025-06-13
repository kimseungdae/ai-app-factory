import React from 'react';
import { BarChart3, Users, TrendingUp, Calendar, Plus, Zap } from 'lucide-react';
import Button from '../common/Button';

const MainScreen = () => {
  const stats = [
    { label: '완료된 작업', value: '24', icon: BarChart3, change: '+12%' },
    { label: '팀 멤버', value: '8', icon: Users, change: '+2' },
    { label: '생산성 향상', value: '32%', icon: TrendingUp, change: '+5%' },
    { label: '오늘 일정', value: '6', icon: Calendar, change: '개' }
  ];
  
  const aiSuggestions = [
    "오후 2시에 마케팅 리뷰 미팅을 예약하는 것이 좋겠어요",
    "내일 오전에 집중도가 높을 시간대입니다. 중요한 작업을 배치해보세요",
    "김팀장님과의 1:1 미팅이 이번 주에 예정되어 있습니다"
  ];
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">ProductivityAI Pro</h1>
            <p className="text-gray-600">AI가 만드는 완벽한 업무 흐름</p>
          </div>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            새 작업
          </Button>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="p-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-sky-500 to-purple-600 rounded-lg text-white p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold mb-2">안녕하세요, 김현수님! 👋</h2>
              <p className="opacity-90">오늘도 효율적인 하루를 만들어보세요.</p>
            </div>
            <Zap className="w-12 h-12 opacity-80" />
          </div>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {stats.map((stat, index) => (
            <div key={index} className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-green-600 mt-1">{stat.change}</p>
                </div>
                <div className="w-12 h-12 bg-sky-100 rounded-lg flex items-center justify-center">
                  <stat.icon className="w-6 h-6 text-sky-600" />
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {/* AI Suggestions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Zap className="w-5 h-5 mr-2 text-sky-500" />
              AI 추천
            </h3>
            <div className="space-y-3">
              {aiSuggestions.map((suggestion, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-sky-50 rounded-lg">
                  <div className="w-2 h-2 rounded-full bg-sky-500 mt-2"></div>
                  <p className="text-sm text-gray-700">{suggestion}</p>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">빠른 작업</h3>
            <div className="space-y-3">
              <Button variant="secondary" className="w-full justify-start">
                <Plus className="w-4 h-4 mr-2" />
                새 프로젝트 생성
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <Users className="w-4 h-4 mr-2" />
                팀원 초대
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <Calendar className="w-4 h-4 mr-2" />
                일정 잡기
              </Button>
              <Button variant="secondary" className="w-full justify-start">
                <BarChart3 className="w-4 h-4 mr-2" />
                분석 보기
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MainScreen;